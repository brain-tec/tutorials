import { Component, useState } from "@odoo/owl";

export class Card extends Component {
    static template = "awesome_owl.Card";
    static props = {
        slots: Object,
    };

    setup() {
        this.state = useState({
            folded: false,
        });
    }

    fold() {
        this.state.folded = !this.state.folded;
    }
}
