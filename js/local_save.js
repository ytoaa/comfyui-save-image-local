import { app } from "../../../scripts/app.js";
import { api } from "../../../scripts/api.js";

app.registerExtension({
    name: "Comfy.LocalSave",
    async setup() {
        // 画像データ受信時のハンドラー
        api.addEventListener("local_save_data", async ({ detail }) => {
            try {
                const { images } = detail;
                
                for (const imageData of images) {
                    const { filename, data, format } = imageData;
                    
                    // Base64データをBlobに変換
                    const response = await fetch(`data:image/${format};base64,${data}`);
                    const blob = await response.blob();
                    
                    // ダウンロードリンクを作成
                    const downloadLink = document.createElement("a");
                    downloadLink.href = URL.createObjectURL(blob);
                    downloadLink.download = filename;
                    
                    // ダウンロードを実行
                    document.body.appendChild(downloadLink);
                    downloadLink.click();
                    document.body.removeChild(downloadLink);
                    URL.revokeObjectURL(downloadLink.href);
                }
                
                // 成功メッセージを表示
                app.ui.dialog.show("Save Complete", `${images.length} image(s) have been downloaded successfully.`);
                
            } catch (error) {
                // エラーメッセージを表示
                app.ui.dialog.show("Save Error", `Error downloading images: ${error.message}`);
            }
        });

        // エラーメッセージのハンドラー
        api.addEventListener("local_save_error", ({ detail }) => {
            app.ui.dialog.show("Save Error", detail.message);
        });
    }
});