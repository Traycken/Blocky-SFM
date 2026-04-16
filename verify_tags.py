from playwright.sync_api import sync_playwright
import os

def run_verify(page):
    path = "file://" + os.path.abspath("sfm-blockly-editor.html")
    page.goto(path)

    # 1. Add a global tag
    page.fill("#newTagName", "MyTag")
    page.click("text=Add")
    page.wait_for_timeout(500)

    # Check if tag exists in script object
    tag_count = page.evaluate("currentScript().tags.length")
    print(f"Global tags count: {tag_count}")

    # 2. Add an Input block
    page.click("text=Trigger")
    page.wait_for_timeout(200)
    page.click("text=+ INPUT")
    page.wait_for_timeout(500)

    # 3. Use the tag picker
    # First, we need to find the tag picker button inside the input block
    page.click("text=MyTag")
    page.wait_for_timeout(500)

    # Check if input block now has the label
    label_value = page.evaluate("blocks[0].children[0].labels")
    print(f"Input block labels: '{label_value}'")

    if label_value != "MyTag":
        raise Exception("Tag picker failed!")

    # 4. Remove the global tag and check if it disappears from the block
    page.click(".gtag .x")
    page.wait_for_timeout(500)

    label_value_after = page.evaluate("blocks[0].children[0].labels")
    print(f"Input block labels after tag removal: '{label_value_after}'")

    if label_value_after != "":
        raise Exception("Tag removal didn't update blocks!")

    page.screenshot(path="verification_tags.png")

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
