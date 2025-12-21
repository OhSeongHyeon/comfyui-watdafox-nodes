import { api } from "../../../scripts/api.js";

api.addEventListener("watdafox-api", (event) => {
	const nodes = app.graph._nodes_by_id;
    const node = nodes[event.detail.node_id];
    if (!node) {
        console.warn(`[watdafox-api] Node not found: ${event.detail.node_id}`);
        return;
    }
    const target_widget = node?.widgets.find((w) => w.name === event.detail["target_widget_name"]);
    if (!target_widget) return;

    // 데이터 타입별(분기) 데이터 정제작업
    const { data_type, data } = event.detail;
    if (data_type === "text") {
        target_widget.value = data; //event.detail.data;
    }
    else {
        // 처리되지 않은 데이터 타입에 대한 경고
        console.warn(`[watdafox-api] Unhandled data_type: ${data_type}`);
        target_widget.value = data; // 기본 동작
    }
});

// 좀 위험해보임...
// api.addEventListener("watdafox-node-fix", (event) => {
// 	const nodes = app.graph._nodes_by_id;
//     const node = nodes[event.detail.node_id];
//     if (!node) {
//         console.warn(`[watdafox-api] Node not found: ${event.detail.node_id}`);
//         return;
//     }
    
//     const target_widgets = event.detail["fix_target_widgets"];
//     target_widgets.forEach((target) => {
//         const target_widget = node?.widgets.find((w) => w.name === target);
//         if (!target_widget) return;

//         const { data_type, data } = event.detail;
//         if (data_type === "json") {
//             if (Array.isArray(data[target])) {
//                 target_widget.value = data[target][0];
//                 target_widget.options.values = data[target];
//             }
//             else {
//                 target_widget.value = data[target];
//             }
//         }
//     });
// });
