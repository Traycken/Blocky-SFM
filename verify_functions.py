from playwright.sync_api import sync_playwright
import os

def run_verify(page):
    path = "file://" + os.path.abspath("sfm-blockly-editor.html")
    page.goto(path)

    # Check if functions exist in window scope
    funcs = ["addStatement", "splitLoose", "escQuote"]
    for func in funcs:
        exists = page.evaluate(f"typeof {func} === 'function'")
        print(f"Function {func} exists: {exists}")
        if not exists:
            raise Exception(f"Function {func} is missing!")

    # Try to add a trigger via palette click
    page.click("text=Trigger")
    page.wait_for_timeout(500)

    # Try to add an input via the + INPUT button inside the trigger zone
    page.click("text=+ INPUT")
    page.wait_for_timeout(500)

    # Check if a block was added
    block_count = page.evaluate("blocks.length")
    print(f"Blocks in root: {block_count}")

    trigger_kids = page.evaluate("blocks[0].children.length")
    print(f"Blocks in trigger: {trigger_kids}")

    if block_count == 0 or trigger_kids == 0:
         raise Exception("Failed to add blocks!")

    page.screenshot(path="verification_final.png")

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
