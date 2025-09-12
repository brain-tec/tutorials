import { registry } from "@web/core/registry";
import { ClickerModel } from "./clicker_model";

const clickerService = {
    dependencies: ["effect"],
    start(env, services) {
        const model = new ClickerModel();

        document.addEventListener("click", () => model.addClick(), true);
        setInterval(() => {
            model.tick();
        }, 10000);
        const bus = model.bus;
        bus.addEventListener("MILESTONE", (ev) => {
            services.effect.add({
                message: `Milestone reached! You can now buy ${ev.detail.unlock}`,
                type: "rainbow_man",
            });
        });

        return model;
    },
};

registry.category("services").add("awesome_clicker.clicker", clickerService);
