import { app } from "../../../scripts/app.js";
import { api } from "../../../scripts/api.js";

app.registerExtension({
    name: "Comfy.LocalSave",
    async setup() {
        // Base64をBlobに変換するユーティリティ関数
        function base64ToBlob(base64, mimeType) {
            // Base64文字列をバイナリデータに変換
            const byteString = atob(base64);
            // バイナリデータをUint8Arrayに変換
            const ab = new ArrayBuffer(byteString.length);
            const ia = new Uint8Array(ab);
            for (let i = 0; i < byteString.length; i++) {
                ia[i] = byteString.charCodeAt(i);
            }
            // Blobを作成して返す
            return new Blob([ab], { type: mimeType });
        }

        // 画像データ受信時のハンドラー
        api.addEventListener("local_save_data", async ({ detail }) => {
            try {
                const { images } = detail;
                
                for (const imageData of images) {
                    const { filename, data, format } = imageData;
                    
                    // Base64データを直接Blobに変換
                    const mimeType = format === 'webp' ? 'image/webp' : `image/${format}`;
                    const blob = base64ToBlob(data, mimeType);
                    
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
                
            } catch (error) {
                // エラーメッセージを表示
                app.ui.dialog.show("Save Error", `Error downloading images: ${error.message}`);
            }
        });

        // エラーメッセージのハンドラー
        api.addEventListener("local_save_error", ({ detail }) => {
            app.ui.dialog.show("Save Error", detail.message);
        });

        // ノード作成時のイベントリスナー
        const originalOnNodeCreated = app.graph.onNodeCreated;
        app.graph.onNodeCreated = (node) => {
            if (node.type === "Local Save") {
                // ノードが完全に初期化된 후にUIを設定
                setTimeout(() => {
                    this.setupNodeUI(node);
                }, 100);
            }
            if (originalOnNodeCreated) {
                originalOnNodeCreated.call(app.graph, node);
            }
        };
        
        // 既存のノードにも適用（安全に列挙）
        setTimeout(() => {
            const nodes = app.graph?._nodes_by_id || [];
            for (const node of nodes) {
                if (node && node.type === "Local Save") {
                    this.setupNodeUI(node);
                }
            }
        }, 500);
    },
    
    setupNodeUI(node) {
        // ファイル形式変更時のイベントリスナー
        const fileFormatWidget = node.widgets.find(w => w.name === "file_format");
        if (fileFormatWidget) {
            const originalCallback = fileFormatWidget.callback;
            fileFormatWidget.callback = (value) => {
                this.updateFormatSpecificUI(node, value);
                if (originalCallback) {
                    originalCallback.call(fileFormatWidget, value);
                }
            };
            
            // 初期表示を更新
            this.updateFormatSpecificUI(node, fileFormatWidget.value);
        }
    },
    
    updateFormatSpecificUI(node, format) {
        // フォーマット固有のウィジェットの表示/非表示を制御
        const formatWidgets = {
            PNG: ["png_compression", "png_optimize"],
            JPEG: ["jpeg_quality", "jpeg_optimize", "jpeg_progressive", "jpeg_subsampling"],
            WEBP: ["webp_quality", "webp_lossless", "webp_method"]
        };
        
        // すべてのフォーマット固有ウィジェットを非表示にする
        Object.values(formatWidgets).flat().forEach(widgetName => {
            const widget = node.widgets.find(w => w.name === widgetName);
            if (widget) {
                // ComfyUIでは type を hidden に設定 + hiddenフラグも設定
                widget.hidden = true;
                widget.type = "hidden";
                // DOM 要素も 숨김
                if (widget.element) {
                    widget.element.style.display = "none";
                    widget.element.style.visibility = "hidden";
                }
                // 親要素も 숨김
                if (widget.element && widget.element.parentElement) {
                    widget.element.parentElement.style.display = "none";
                }
            }
        });
        
        // 選択されたフォーマットのウィジェットを表示する
        if (formatWidgets[format]) {
            formatWidgets[format].forEach(widgetName => {
                const widget = node.widgets.find(w => w.name === widgetName);
                if (widget) {
                    // 元のタイプを復元
                    if (widgetName.includes("compression") || widgetName.includes("quality") || widgetName.includes("method")) {
                        widget.type = "number";
                    } else if (widgetName.includes("optimize") || widgetName.includes("progressive") || widgetName.includes("lossless")) {
                        widget.type = "toggle";
                    } else if (widgetName.includes("subsampling")) {
                        widget.type = "combo";
                    }
                    widget.hidden = false;
                    
                    // DOM 要素도 표시
                    if (widget.element) {
                        widget.element.style.display = "";
                        widget.element.style.visibility = "visible";
                    }
                    // 親要素도 표시
                    if (widget.element && widget.element.parentElement) {
                        widget.element.parentElement.style.display = "";
                    }
                }
            });
        }
        
        // UIを再描画
        node.setDirtyCanvas(true, true);
        
        // ノードの 크기를再計算
        if (node.computeSize) {
            node.computeSize();
        }
        
        // 強制的に再描画
        setTimeout(() => {
            node.setDirtyCanvas(true, true);
        }, 50);
    }
});