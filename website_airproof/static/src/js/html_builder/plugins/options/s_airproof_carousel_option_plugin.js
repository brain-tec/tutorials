import { Plugin } from "@html_editor/plugin";
import { registry } from "@web/core/registry";
import { BuilderAction } from "@html_builder/core/builder_action";

class CarouselBubbleOptionPlugin extends Plugin {
    static id = "carouselBubbleOption";
    resources = {
        builder_options: [
           {
                template: "website_airproof.CarouselBubbleOption",
                selector: ".x_bubble_item",
            },
        ],
        builder_actions: {
            BubbleMarginAction,
        }
    };
}

export class SetBubbleMarginAction extends BuilderAction {
    static id = "setBubbleMargin";
    getValue({editingElement}) {
        const match = [...editingElement.classList].join(" ").match(/mb-(\d+)/);

        if (match) {
            return Number(match[1]);
        }

        return 0;
    }

    apply({ editingElement, value }) {
        editingElement.classList.forEach(classSelector => {
            if (classSelector.startsWith("mb-")) {
                editingElement.classList.remove(classSelector);
            }
        });

        editingElement.classList.add(`mb-${value}`);
    }
}

registry.category("website-plugins").add(CarouselBubbleOptionPlugin.id, CarouselBubbleOptionPlugin);
