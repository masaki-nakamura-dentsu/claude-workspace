#!/usr/bin/env python3
"""
汎用PDF軽量化ツール(画像解像度を落としてファイルサイズを縮小)

写真集/小冊子など、写真をたくさん含むPDFを「確認用」の軽いファイルにするための
汎用スクリプト。Ghostscriptで画像を指定dpiに再サンプリングして再圧縮するだけで、
ページのレイアウト・トリムサイズなどは一切変更しない。

個人Mac(ICPTokyo2022)・会社Mac(d14461)の両方で使えるように、
Dropbox同期フォルダ(.claude-sync/Scripts/)に置いている。
~/Scripts/pdf_shrink.py はこのファイルへのシンボリックリンク。

使い方:
    python3 pdf_shrink.py 入力.pdf                    # デフォルト100dpiで圧縮
    python3 pdf_shrink.py 入力.pdf --dpi 150
    python3 pdf_shrink.py 入力.pdf -o 出力.pdf
    python3 pdf_shrink.py 入力.pdf --preset ebook      # プリセットを変える

必要なもの: Ghostscript (gs コマンド)
    未インストールの場合: brew install ghostscript
"""

import argparse
import re
import shutil
import subprocess
import sys
from pathlib import Path

PRESETS = ("screen", "ebook", "printer", "prepress", "default")


def check_ghostscript() -> None:
    if shutil.which("gs") is None:
        sys.exit(
            "エラー: Ghostscript (gs コマンド) が見つかりません。\n"
            "  brew install ghostscript\n"
            "でインストールしてから再実行してください。"
        )


def count_pages(pdf_path: Path) -> int | None:
    """依存ライブラリなしでざっくりページ数を数える(整合性チェック用)。"""
    try:
        data = pdf_path.read_bytes()
    except OSError:
        return None
    return len(re.findall(rb"/Type\s*/Page[^s]", data))


def shrink_pdf(input_path: Path, output_path: Path, dpi: int, preset: str) -> None:
    cmd = [
        "gs",
        "-sDEVICE=pdfwrite",
        "-dCompatibilityLevel=1.4",
        f"-dPDFSETTINGS=/{preset}",
        f"-dColorImageResolution={dpi}",
        f"-dGrayImageResolution={dpi}",
        f"-dMonoImageResolution={dpi}",
        "-dNOPAUSE",
        "-dBATCH",
        "-dQUIET",
        f"-sOutputFile={output_path}",
        str(input_path),
    ]
    subprocess.run(cmd, check=True)


def main() -> None:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("input", type=Path, help="入力PDF")
    parser.add_argument("-o", "--output", type=Path, help="出力PDFパス(省略時は自動命名)")
    parser.add_argument("--dpi", type=int, default=100, help="画像解像度(デフォルト100dpi)")
    parser.add_argument(
        "--preset", choices=PRESETS, default="screen", help="Ghostscript PDFSETTINGS(デフォルトscreen)"
    )
    args = parser.parse_args()

    check_ghostscript()

    if not args.input.exists():
        sys.exit(f"入力ファイルが見つかりません: {args.input}")

    output_path = args.output or args.input.with_name(f"{args.input.stem}_{args.dpi}dpi{args.input.suffix}")

    before_bytes = args.input.stat().st_size
    before_pages = count_pages(args.input)

    shrink_pdf(args.input, output_path, args.dpi, args.preset)

    after_bytes = output_path.stat().st_size
    after_pages = count_pages(output_path)

    if before_pages is not None and after_pages is not None and before_pages != after_pages:
        print(
            f"警告: ページ数が変わっています(元 {before_pages} → 出力 {after_pages})。"
            "出力を目視確認してください。",
            file=sys.stderr,
        )

    reduction = (1 - after_bytes / before_bytes) * 100 if before_bytes else 0
    print(
        f"完了: {output_path}\n"
        f"  {before_bytes/1024/1024:.1f} MB → {after_bytes/1024/1024:.1f} MB "
        f"({reduction:.1f}%削減)"
    )


if __name__ == "__main__":
    main()
