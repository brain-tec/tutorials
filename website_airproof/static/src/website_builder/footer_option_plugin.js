import { Plugin } from "@html_editor/plugin";
import { registry } from "@web/core/registry";
import { _t } from "@web/core/l10n/translation";
import { FooterTemplateChoice } from "@website/builder/plugins/options/footer_template_option";

export class AirproofFooterOptionPlugin extends Plugin {
    static id = "airproofFooteOption";
    resources = {
        footer_templates_providers: () => [
        {
            key: "airproof",
            Component: FooterTemplateChoice,
            props: {
                title: _t("Airproof"),
                view: "website_airproof.footer",
                varName: "airproof",
                imgSrc: "/website_airproof/static/src/img/wbuilder/template-footer-opt.svg",
            },
        },
        ],
    };
}

registry.category("website-plugins").add(AirproofFooterOptionPlugin.id, AirproofFooterOptionPlugin);
