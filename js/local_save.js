import { app } from "../../../scripts/app.js";
import { api } from "../../../scripts/api.js";

app.registerExtension({
    name: "Comfy.LocalSave",
    async setup() {
        // 保存完了メッセージのハンドラー
        api.addEventListener("local_save_complete", ({ detail }) => {
            // 成功メッセージの表示
            app.ui.dialog.show(`Save Complete`, detail.message);
        });

        // エラーメッセージのハンドラー
        api.addEventListener("local_save_error", ({ detail }) => {
            // エラーメッセージの表示
            app.ui.dialog.show(`Save Error`, detail.message);
        });
    }
});