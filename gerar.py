#!/usr/bin/env python3
"""Gera card (PNG 1080x1350) ou Reels (MP4 1080x1920 com música) a partir de um JSON.

Uso:  python3 gerar.py specs/2026-10-29-chuveiro.json
Saída: cards/<arquivo>.png  ou  reels/<arquivo>.mp4

Formato do JSON (veja specs/exemplo-card.json e specs/exemplo-reel.json):
  tipo        "card" ou "reel"
  arquivo     nome do arquivo sem extensão, ex. "2026-10-29-chuveiro"
  etiqueta    texto curto da etiqueta amarela (ex. "Alerta", "Dica de eletricista")
  titulo      lista de 2 a 3 linhas; trecho entre **asteriscos** fica amarelo
  subtitulo   uma frase curta
  itens       2 a 4 itens; trecho entre **asteriscos** fica amarelo/negrito
  cta         card: frase final, **trecho** em amarelo | reel: frase do rodapé
  alerta      (só reel, opcional) frase de aviso em caixa vermelha; **trecho** destacado
  musica      (só reel, opcional) número da variação de trilha, 0 a 3
  tema        (só reel, opcional) "escuro" (padrão) ou "amarelo"

Layouts de card (campo "layout", padrão "lista"):
  lista     etiqueta, titulo, subtitulo, itens (3), cta            fundo azul escuro
  pergunta  etiqueta, titulo (pergunta em 3-4 linhas curtas),
            resposta (2 a 3 frases), cta                         fundo amarelo
  mito      etiqueta (assunto), mito (frase errada que o povo
            fala), verdade (a correção), cta                     fundo claro
  numero    etiqueta, numero (ex. "30"), unidade (ex. "mA"),
            titulo (2-3 linhas explicando o número), itens (2), cta   fundo azul com número gigante
  Use só números técnicos reais (norma, especificação); nunca invente estatística.
"""
import html, json, os, re, shutil, subprocess, sys, tempfile
import numpy as np, wave
from playwright.sync_api import sync_playwright

BASE = os.path.dirname(os.path.abspath(__file__))


def fmt(texto, tag_destaque):
    t = html.escape(texto)
    return re.sub(r"\*\*(.+?)\*\*", lambda m: tag_destaque.format(m.group(1)), t)


LAYOUTS_CARD = {"lista": "card.html", "pergunta": "card-pergunta.html", "mito": "card-mito.html", "numero": "card-numero.html"}


def montar_card_especial(spec):
    """Layouts de card além da lista: pergunta, mito e numero."""
    layout = spec["layout"]
    modelo = open(os.path.join(BASE, "modelos", LAYOUTS_CARD[layout]), encoding="utf-8").read()
    titulo = "".join('<span class="l">%s</span>' % fmt(l, "<span class=y>{}</span>") for l in spec.get("titulo", []))
    itens = "".join('<div class="item"><div>%s</div></div>' % fmt(it, "<b>{}</b>") for it in spec.get("itens", []))
    numero = html.escape(spec.get("numero", ""))
    if spec.get("unidade"):
        numero += "<small>%s</small>" % html.escape(spec["unidade"])
    destaque_cta = "<b>{}</b>" if layout == "mito" else "{}"
    subs = {
        "{{ETIQUETA}}": html.escape(spec.get("etiqueta", "")),
        "{{TITULO}}": titulo,
        "{{RESPOSTA}}": fmt(spec.get("resposta", ""), "<b>{}</b>"),
        "{{MITO}}": fmt(spec.get("mito", ""), "{}"),
        "{{VERDADE}}": fmt(spec.get("verdade", ""), "<b>{}</b>"),
        "{{NUMERO}}": numero,
        "{{ITENS}}": itens,
        "{{CTA}}": fmt(spec.get("cta", ""), destaque_cta),
    }
    for k, v in subs.items():
        modelo = modelo.replace(k, v)
    return modelo, 0


def montar_html(spec):
    reel = spec["tipo"] == "reel"
    if not reel and spec.get("layout", "lista") != "lista":
        return montar_card_especial(spec)
    modelo = open(os.path.join(BASE, "modelos", "reel.html" if reel else "card.html"), encoding="utf-8").read()
    modelo = modelo.replace("{{TEMA}}", "amarelo" if spec.get("tema") == "amarelo" else "escuro")
    linhas = spec["titulo"]
    t_lin = [0.35 + 0.2 * i for i in range(len(linhas))]
    titulo = ""
    for l, t in zip(linhas, t_lin):
        atraso = ' style="animation-delay:%.2fs"' % t if reel else ""
        titulo += '<span class="l"%s>%s</span>' % (atraso, fmt(l, "<span class=y>{}</span>"))
    t_sub = t_lin[-1] + 0.8
    t_item0 = t_sub + 1.3
    itens = ""
    for i, it in enumerate(spec["itens"]):
        atraso = f' style="animation-delay:{t_item0 + 1.5 * i:.2f}s"' if reel else ""
        itens += f'<div class="item"{atraso}><div class="num">{i+1}</div><div>{fmt(it, "<b>{}</b>")}</div></div>'
    t_ult = t_item0 + 1.5 * (len(spec["itens"]) - 1)
    alerta = spec.get("alerta")
    t_warn = t_ult + 1.9
    t_foot = (t_warn + 1.7) if alerta else (t_ult + 2.2)
    dur = round(t_foot + 2.7, 2)
    if reel:
        cta = html.escape(spec["cta"].replace("**", ""))
    else:
        cta = fmt(spec["cta"], "<br><b>{}</b>")
    subs = {
        "{{ETIQUETA}}": html.escape(spec["etiqueta"]),
        "{{TITULO}}": titulo,
        "{{SUBTITULO}}": fmt(spec["subtitulo"], "<span class=y>{}</span>"),
        "{{ITENS}}": itens,
        "{{CTA}}": cta,
        "{{ALERTA}}": f'<div class="warn">{fmt(alerta, "<b>{}</b>")}</div>' if alerta else "",
        "{{DUR}}": f"{dur}", "{{T_SUB}}": f"{t_sub:.2f}", "{{T_WARN}}": f"{t_warn:.2f}",
        "{{T_WARN2}}": f"{t_warn + 0.5:.2f}", "{{T_FOOT}}": f"{t_foot:.2f}",
    }
    for k, v in subs.items():
        modelo = modelo.replace(k, v)
    return modelo, dur


def ajustar_tamanho(pg, reel):
    """Reduz o zoom do conteúdo até ele não encostar no rodapé."""
    if reel:
        pg.evaluate("document.getAnimations().forEach(a=>{a.pause(); a.currentTime=1e6})")
    z = 1.0
    while z > 0.6:
        sobra = pg.evaluate(
            "document.getElementById('rodape').getBoundingClientRect().top - document.getElementById('conteudo').getBoundingClientRect().bottom"
        )
        if sobra >= 40:
            break
        z = round(z - 0.04, 2)
        pg.evaluate(f"document.documentElement.style.setProperty('--z','{z}')")
    return z


def musica(caminho, dur, variacao=0):
    SR = 44100
    progs = [[[57, 60, 64], [53, 57, 60], [48, 52, 55], [55, 59, 62]],
             [[48, 52, 55], [55, 59, 62], [57, 60, 64], [53, 57, 60]],
             [[50, 53, 57], [55, 58, 62], [53, 57, 60], [57, 61, 64]],
             [[52, 55, 59], [48, 52, 55], [55, 59, 62], [50, 54, 57]]]
    bpm = [100, 96, 104, 92][variacao % 4]
    chords = progs[variacao % 4]
    beat = 60 / bpm; bar = beat * 4
    t = np.arange(int(SR * dur)) / SR
    out = np.zeros_like(t)
    f = lambda n: 440 * 2 ** ((n - 69) / 12)
    for i in range(int(dur / bar) + 1):
        s = i * bar; ch = chords[i % 4]
        idx = (t >= s) & (t < s + bar + 0.3); tt = t[idx] - s
        env = np.minimum(tt / 0.4, 1) * np.exp(-tt * 0.35)
        for n in ch:
            out[idx] += 0.06 * env * (np.sin(2*np.pi*f(n)*tt) + 0.3*np.sin(4*np.pi*f(n)*tt) + 0.15*np.sin(2*np.pi*f(n)*1.003*tt))
        out[idx] += 0.10 * env * np.sin(2*np.pi*f(ch[0]-12)*tt)
    rng = np.random.default_rng(7)
    for k in range(int(dur / beat) + 1):
        s = k * beat
        if s < 0.9:
            continue
        i0 = int(s * SR); L = int(0.25 * SR); tt = np.arange(L) / SR
        seg = out[i0:i0+L]; seg += (np.sin(2*np.pi*(55+90*np.exp(-tt*30))*tt) * np.exp(-tt*14) * 0.35)[:len(seg)]
        h0 = int((s + beat/2) * SR); H = int(0.06 * SR)
        seg = out[h0:h0+H]; seg += (rng.standard_normal(H) * np.exp(-np.arange(H)/SR*70) * 0.035)[:len(seg)]
    fim = t > dur - 1.2; out[fim] *= np.linspace(1, 0, fim.sum())
    ini = t < 0.3; out[ini] *= np.linspace(0, 1, ini.sum())
    out = out / np.max(np.abs(out)) * 0.7
    w = wave.open(caminho, "wb"); w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((out * 32767).astype(np.int16).tobytes()); w.close()


def gerar(spec_path):
    spec = json.load(open(spec_path, encoding="utf-8"))
    reel = spec["tipo"] == "reel"
    pagina, dur = montar_html(spec)
    tmp = tempfile.mkdtemp()
    html_path = os.path.join(tmp, "p.html")
    open(html_path, "w", encoding="utf-8").write(pagina)
    w, h = (1080, 1920) if reel else (1080, 1350)
    pasta = os.path.join(BASE, "reels" if reel else "cards")
    os.makedirs(pasta, exist_ok=True)
    with sync_playwright() as p:
        b = p.chromium.launch(); pg = b.new_page(viewport={"width": w, "height": h})
        pg.goto("file://" + html_path); pg.wait_for_timeout(400)
        z = ajustar_tamanho(pg, reel)
        if not reel:
            saida = os.path.join(pasta, spec["arquivo"] + ".png")
            pg.screenshot(path=saida)
        else:
            os.makedirs(os.path.join(tmp, "f"))
            fps = 30
            for i in range(int(fps * dur)):
                pg.evaluate(f"document.getAnimations().forEach(a=>{{a.pause(); a.currentTime={i*1000/fps}}})")
                pg.screenshot(path=os.path.join(tmp, "f", f"{i:04d}.png"))
        b.close()
    if reel:
        wav = os.path.join(tmp, "m.wav"); musica(wav, dur, spec.get("musica", 0))
        saida = os.path.join(pasta, spec["arquivo"] + ".mp4")
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", "30", "-i", os.path.join(tmp, "f", "%04d.png"),
                        "-i", wav, "-c:v", "libx264", "-pix_fmt", "yuv420p", "-profile:v", "high", "-crf", "20",
                        "-c:a", "aac", "-b:a", "128k", "-shortest", "-movflags", "+faststart", saida], check=True)
        capa = os.path.join(pasta, spec["arquivo"] + "-capa.png")
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-sseof", "-1", "-i", saida, "-frames:v", "1", capa], check=True)
    shutil.rmtree(tmp, ignore_errors=True)
    print(f"OK {saida} (zoom {z}{f', {dur}s' if reel else ''})")


if __name__ == "__main__":
    for arg in sys.argv[1:]:
        gerar(arg)
