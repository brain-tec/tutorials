import { Component, useState, useRef, onMounted } from "@odoo/owl";
import { TodoItem } from "./todo_item";

function useAutofocus(refName) {
    const ref = useRef(refName);
    onMounted(() => {
        ref.el.focus();
    });
}

export class TodoList extends Component {
    static template = "awesome_owl.TodoList";
    static components = { TodoItem };

    setup() {
        useAutofocus("inputref");
        this.todos = useState([]);
    }

    addTodo(ev) {
        if (ev.keyCode === 13) {
            if (!ev.target.value.trim()) {
                return;
            }
            this.todos.push({
                id: this.todos.length + 1,
                description: ev.target.value,
                isCompleted: false,
            });
            ev.target.value = "";
        }
    }
}
