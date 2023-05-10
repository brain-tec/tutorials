import { Component, markup, useState } from "@odoo/owl";
import { Counter } from "./counter/counter";
import { Card } from "./card/card";
import { TodoList } from "./todo_list/todo_list";

export class Playground extends Component {
    static template = "awesome_owl.playground";
    static components = { Counter, Card, TodoList };

    setup() {
        this.str1 = "<div class='text-primary'>some content</div>";
        this.str2 = markup("<div class='text-primary'>some content</div>");
        this.values = useState([1,2,3,4,5,6,7,8,9]);
    }

    get sum() {
        let sum = 0;
        for (let val of this.values) {
            sum += val;
        }
        return sum;
    }

    incrementValue(index) {
        this.values[index]++;
    }
}
