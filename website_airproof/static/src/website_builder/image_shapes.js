import {Plugin} from "@html_editor/plugin";
import {_t} from "@web/core/l10n/translation";
import {registry} from "@web/core/registry";
export class AirproofImageShapesPlugin extends Plugin {
    static id = "airproofImageShapes";
    resources = {
        image_shape_groups_providers: () => ({
            airproof: {
                label: _t("Airproof"),
                subgroups: {
                    airproof: {
                        label: _t("Duo"),
                        shapes: {
                            "website_airproof/duo/01": {
                                selectLabel: _t("Airproof 01"),
                                transform: true,
                                togglableRatio: true,
                            },
                        },
                    },
                },
            },
        }),
    };
}

registry.category("website-plugins").add(AirproofImageShapesPlugin.id, AirproofImageShapesPlugin);
