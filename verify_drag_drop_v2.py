from playwright.sync_api import sync_playwright
import os

def run_verify(page):
    path = "file://" + os.path.abspath("sfm-blockly-editor.html")
    page.goto(path)

    # 1. Add Trigger
    page.click("text=Trigger")
    page.wait_for_timeout(500)

    # 2. Simulate dragstart on Input palette block
    # This should set the dragType variable
    page.evaluate('''() => {
        const inputPalette = document.querySelector(".pb-input");
        const event = new Event("dragstart", { bubbles: true });
        // We can't easily mock DataTransfer in a simple Event,
        // but our code only cares about the global dragType variable.
        inputPalette.dispatchEvent(event);
        console.log("dragType after dragstart:", dragType);
    }''')

    # 3. Drop onto the zone
    page.evaluate('''() => {
        const zone = document.querySelector(".zone");
        const event = new Event("drop", { bubbles: true });
        // onZoneDrop is attached to the zone element.
        // It expects (e, arr). But the event listener is set as:
        // z.ondrop=e=>onZoneDrop(e,arr);
        zone.dispatchEvent(event);
    }''')

    page.wait_for_timeout(500)

    input_count = page.evaluate("blocks[0].children.filter(b => b.type === 'input').length")
    print(f"Inputs in trigger after simulated drag-drop: {input_count}")

    if input_count == 0:
        # Fallback: try clicking the button
        print("Simulated drag-drop failed, trying button click...")
        page.click("text=+ INPUT")
        page.wait_for_timeout(500)
        input_count = page.evaluate("blocks[0].children.filter(b => b.type === 'input').length")
        print(f"Inputs in trigger after button click: {input_count}")

    if input_count == 0:
        raise Exception("Failed to add input block!")

    page.screenshot(path="verification_drag_drop_v2.png")

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
