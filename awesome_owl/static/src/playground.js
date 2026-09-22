import { Component, useState, markup } from "@odoo/owl";
import { Counter } from "./counter/counter";
import { Card } from "./card/card";
import { TodoList } from "./todo_list/todo_list";

export class Playground extends Component {
    static template = "awesome_owl.playground";
    static components = { Counter, Card, TodoList };

    setup() {
        this.str = "Some <b>text</b>";
        this.html = markup("Some <b>html text</b>");
        this.state = useState({ sum: 0 });
    }

    incrementSum() {
        this.state.sum++;
    }
}
