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

// 좀 위험...???
// 사용 로컬마다 yaml 파일 다를 경우 노드위젯 교정시도
api.addEventListener("watdafox-node-fix", (event) => {
	const nodes = app.graph._nodes_by_id;
    const node = nodes[event.detail.node_id];
    if (!node) {
        console.warn(`[watdafox-node-fix] Node not found: ${event.detail.node_id}`);
        return;
    }
    console.warn('[watdafox-node-fix] Attempted node widget calibration');

    const target_widgets = event.detail["fix_target_widgets"];
    target_widgets.forEach((target) => {
        const target_widget = node?.widgets.find((w) => w.name === target);
        if (!target_widget) return;

        const { data_type, data } = event.detail;
        if (data_type === "json") {
            if (Array.isArray(data[target])) {
                target_widget.value = data[target][0];
                target_widget.options.values = data[target];
            }
            else {
                target_widget.value = data[target];
            }
        }
    });
});
