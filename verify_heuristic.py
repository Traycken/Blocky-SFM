from playwright.sync_api import sync_playwright
import os

def run_verify(page):
    path = "file://" + os.path.abspath("sfm-blockly-editor.html")
    page.goto(path)

    code = """NAME "Test Heuristic"
EVERY 20 TICKS DO
    INPUT
        RETAIN 8 coal,
        RETAIN 16 *_log WITH TAG minecraft:logs
    FROM fuel_chest
    OUTPUT 1 coal TO furnace
END"""

    # Use heuristicParseSFM
    page.evaluate(f'''() => {{
        const s = heuristicParseSFM();
        app.scripts.unshift(s);
        openScript(s.id);
    }}''')
    page.wait_for_timeout(500)

    # Verify blocks
    blocks_count = page.evaluate("blocks.length")
    print(f"Blocks count: {blocks_count}")

    trigger_kids = page.evaluate("blocks[0].children.length")
    print(f"Blocks in trigger: {trigger_kids}")

    input_limits = page.evaluate("blocks[0].children[0].limits.length")
    print(f"Input limits count: {input_limits}")

    input_labels = page.evaluate("blocks[0].children[0].labels")
    print(f"Input labels: {input_labels}")

    if blocks_count != 1 or trigger_kids != 2 or input_limits != 2:
        raise Exception("Heuristic parse failed to reconstruct structure!")

    page.screenshot(path="verification_heuristic.png")

if __name__ == "__main__":
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()
        try:
            run_verify(page)
        finally:
            context.close()
            browser.close()
