import {Plugin} from "@html_editor/plugin";
import {_t} from "@web/core/l10n/translation";
import {registry} from "@web/core/registry";
export class AirproofBackgroundShapesPlugin extends Plugin {
    static id = "airproofBackgroundShapesOption";
    resources = {
        background_shape_groups_providers: () => ({
            airproof: {
                label: _t("Airproof"),
                subgroups: {
                    airproof: {
                        label: _t("Airproof"),
                        shapes: {
                            "website_airproof/waves/01": {
                                selectLabel: _t("Airproof 01"),
                            },
                        },
                    },
                },
            },
        }),
    };
}

registry.category("website-plugins").add(
    AirproofBackgroundShapesPlugin.id,
    AirproofBackgroundShapesPlugin
);
