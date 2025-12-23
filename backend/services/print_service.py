from pathlib import Path


def generate_png_with_playwright(servico, out_path, app):
    """Generate a PNG of the rendered `nota.html` for a given service using Playwright.

    Arguments:
        servico: Servico model instance
        out_path: destination file path for PNG
        app: Flask app instance

    Raises:
        RuntimeError: if Playwright is not installed or generation fails
    """
    try:
        from playwright.sync_api import sync_playwright
    except Exception as e:
        raise RuntimeError("Playwright is not installed. Install with: pip install playwright\nThen run: python -m playwright install chromium") from e

    # Render the HTML + inline CSS so page.set_content works offline
    from flask import render_template
    base_url = app.static_folder
    # Try multiple css locations (root and /css folder)
    css_text = ''
    css_candidates = [
        Path(base_url) / 'css' / 'site.css',
        Path(base_url) / 'site.css'
    ]
    for p in css_candidates:
        if p.exists():
            try:
                css_text += '\n' + p.read_text(encoding='utf-8')
            except Exception:
                pass

    # Render template inside a request context so url_for and external URLs work
    with app.test_request_context('/', base_url='http://localhost'):
        full_html = render_template('nota.html', servico=servico)

    # Extract only the .nota element to avoid capturing site chrome (navbar/sidebar)
    def extract_div_by_class(haystack, class_name):
        start_token = f'<div class="{class_name}'
        start = haystack.find(start_token)
        if start == -1:
            # fallback: try simple search for opening tag
            start = haystack.find(f'<div class="{class_name}"')
            if start == -1:
                return None
        # find the first '<div' before the class occurrence
        div_start = haystack.rfind('<div', 0, start)
        if div_start == -1:
            div_start = start
        idx = div_start
        depth = 0
        while idx < len(haystack):
            next_open = haystack.find('<div', idx)
            next_close = haystack.find('</div>', idx)
            if next_open == -1 and next_close == -1:
                break
            if next_open != -1 and next_open < next_close:
                depth += 1
                idx = next_open + 4
            else:
                depth -= 1
                idx = next_close + 6
                if depth <= 0:
                    # include the closing tag
                    return haystack[div_start:idx]
        return None

    nota_fragment = extract_div_by_class(full_html, 'nota')

    # Build a minimal HTML document containing only the note, with inline CSS
    minimal_html = None
    if nota_fragment:
        minimal_html = f"""<!doctype html>
<html lang=\"pt-br\">
<head>
<meta charset=\"utf-8\">
<meta name=\"viewport\" content=\"width=device-width,initial-scale=1\">
<title>Nota {servico.id}</title>
<style>{css_text}</style>
<base href=\"http://localhost/\">
</head>
<body>
{nota_fragment}
</body>
</html>
"""
    else:
        # fallback to full HTML if extraction failed
        minimal_html = full_html
        if '</head>' in minimal_html and css_text:
            minimal_html = minimal_html.replace('</head>', f'<style>{css_text}</style></head>')
        elif css_text:
            minimal_html = f'<style>{css_text}</style>' + minimal_html
        if '</head>' in minimal_html:
            minimal_html = minimal_html.replace('</head>', '<base href="http://localhost/">\n</head>')
        else:
            minimal_html = f'<base href="http://localhost/">\n' + minimal_html

    html = minimal_html

    # Write rendered HTML and css snippet to exports for debugging
    try:
        exports_dir = Path(app.config.get('EXPORTS_PATH') or Path('.'))
        exports_dir.mkdir(parents=True, exist_ok=True)
        rendered_path = exports_dir / f'nota_{servico.id}_rendered.html'
        rendered_path.write_text(html, encoding='utf-8')
        css_dump_path = exports_dir / f'nota_{servico.id}_css.txt'
        css_dump_path.write_text(css_text or '', encoding='utf-8')
    except Exception:
        pass

    # Use Playwright to render the HTML and take a full-page screenshot
    import traceback, shutil
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch()
            # Use a higher-resolution viewport for better print quality (2x scale)
            scale = 2
            vw = 1240 * scale
            vh = 1754 * scale
            page = browser.new_page(viewport={"width": vw, "height": vh})
            # set_content will load the inline CSS as long as we injected it above
            page.set_content(html, wait_until='load')
            page.wait_for_load_state('networkidle')

            # Ensure CSS is injected via Playwright API as a fallback
            css_injected = False
            try:
                if css_text:
                    page.add_style_tag(content=css_text)
                    css_injected = True
            except Exception:
                css_injected = False

            # emulate screen media so screen CSS rules apply during screenshot
            try:
                page.emulate_media(media='screen')
            except Exception:
                pass

            # wait for fonts to be ready and a short delay to let layout settle
            try:
                page.wait_for_function('document.fonts && document.fonts.ready', timeout=5000)
            except Exception:
                pass
            page.wait_for_timeout(1500)
            page.locator('body').wait_for(state='visible', timeout=7000)

            # Prefer capturing only the .nota element to avoid page chrome and ensure CSS is applied to it
            element_screenshot = False
            element_box = None
            try:
                nota_locator = page.locator('.nota')
                nota_locator.wait_for(state='visible', timeout=5000)
                # try element screenshot (more reliable for print layout)
                nota_locator.screenshot(path=str(out_path))
                element_screenshot = True
                # collect bounding info for debug
                element_box = page.evaluate("() => { const el = document.querySelector('.nota'); if (!el) return null; const r = el.getBoundingClientRect(); return {x: r.x, y: r.y, width: r.width, height: r.height, scrollHeight: el.scrollHeight}; }")
            except Exception:
                element_screenshot = False

            if not element_screenshot:
                # fallback to full page screenshot
                page.screenshot(path=str(out_path), full_page=True)

            # write a small debug file about CSS injection, resolution and element usage
            try:
                exports_dir = Path(app.config.get('EXPORTS_PATH') or Path('.'))
                debug_file = exports_dir / f'nota_{servico.id}_screenshot_debug.txt'
                with debug_file.open('w', encoding='utf-8') as df:
                    df.write(f'css_injected: {css_injected}\n')
                    df.write(f'viewport: {vw}x{vh}\n')
                    df.write(f'element_screenshot: {element_screenshot}\n')
                    df.write(f'element_box: {element_box}\n')
                    df.write(f'out_path: {out_path}\n')
            except Exception:
                pass
            browser.close()

        # After successful screenshot, ensure both canonical and _playwright variants exist
        try:
            out_p = Path(out_path)
            exports_dir = Path(app.config.get('EXPORTS_PATH') or Path('.'))
            canonical = exports_dir / f'nota_{servico.id}.png'
            alt = exports_dir / f'nota_{servico.id}_playwright.png'
            # copy to both names depending on which was generated
            if out_p.exists():
                # create both variants
                shutil.copyfile(out_p, canonical)
                shutil.copyfile(out_p, alt)
        except Exception:
            pass

    except Exception as e:
        # write traceback to exports for easier debugging
        try:
            exports_dir = Path(app.config.get('EXPORTS_PATH') or Path('.'))
            exports_dir.mkdir(parents=True, exist_ok=True)
            log_path = exports_dir / f'print_error_{servico.id}.log'
            with log_path.open('w', encoding='utf-8') as f:
                f.write('Playwright generation error:\n')
                traceback.print_exc(file=f)
        except Exception:
            # if logging fails, ignore to not mask original error
            pass
        raise

    return out_path
