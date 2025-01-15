[English](./README.md) | 日本語

# ComfyUI Local Save Node

ComfyUIで生成した画像をローカルPCに直接ダウンロードするためのカスタムノードです。

## 機能

- ComfyUIで生成した画像をローカルPCに直接保存
- PNGまたはJPEG形式でのダウンロードをサポート
- カスタマイズ可能なファイル名プレフィックス
- タイムスタンプと連番を含むファイル名の自動生成
- バッチ処理による複数画像の一括ダウンロード
- 保存完了時のフィードバック表示

## インストール方法

1. ComfyUIのカスタムノードディレクトリに移動:
```bash
cd ComfyUI/custom_nodes
```

2. このリポジトリをクローン:
```bash
git clone https://github.com/your-username/comfyui_local_save.git
```

3. ComfyUIを再起動

## 使用方法

1. ComfyUIのノードブラウザで "Local Save Image" を検索

2. ノードを追加し、以下のパラメータを設定:
   - `prefix`: 保存するファイル名のプレフィックス（デフォルト: "generated"）
   - `file_format`: 保存形式を選択（PNG/JPEG）

3. 画像生成ノードの出力を "Local Save Image" ノードの入力に接続

4. ワークフローを実行すると、生成された画像が自動的にダウンロードされます

## ファイル名形式

保存される画像のファイル名は以下の形式で生成されます：
```
{prefix}_{timestamp}_{number}.{ext}
```

例：
```
generated_20250115_112814_001.png
generated_20250115_112814_002.png
```

- `prefix`: ユーザーが指定したプレフィックス
- `timestamp`: YYYYMMdd_HHmmss形式のタイムスタンプ
- `number`: 001から始まる3桁の連番
- `ext`: 選択した形式（png/jpeg）

## 注意事項

- ブラウザの設定によっては、複数ファイルのダウンロードが制限される場合があります
- 大量の画像を一度に処理する場合、メモリ使用量にご注意ください
- JPEG形式を選択した場合、品質は95%に設定されています

## ライセンス

[MIT License](LICENSE)

## 開発者向け情報

依存パッケージ:
```
torch>=2.0.0
Pillow>=9.0.0
numpy>=1.22.0
```

これらのパッケージはComfyUIの標準インストールに含まれています。

## お問い合わせ

バグ報告や機能リクエストは、GitHubのIssueにてお願いします。