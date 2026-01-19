#!/usr/bin/env python3
"""デバッグ用スクリプト - 各機能を個別にテストする"""

import argparse
from chat import SimpleChat


def test_add_message(message: str, model: str = "gpt-4o-mini"):
    """SimpleChat.add_message() のテスト"""
    print(f"=== SimpleChat.add_message() テスト ===")
    print(f"Model: {model}")
    print(f"Input: {message}")
    print("-" * 50)

    chat = SimpleChat(model=model)
    response = chat.add_message(message)

    print(f"Response: {response}")
    print("-" * 50)
    chat.print_history()

    return response


def main():
    parser = argparse.ArgumentParser(description="機能別デバッグスクリプト")
    subparsers = parser.add_subparsers(dest="command", help="テストする機能")

    # add_message コマンド
    add_msg_parser = subparsers.add_parser("add_message", help="SimpleChat.add_message() をテスト")
    add_msg_parser.add_argument("message", type=str, help="送信するメッセージ")
    add_msg_parser.add_argument("--model", type=str, default="gpt-4o-mini", help="使用するモデル")

    args = parser.parse_args()

    if args.command == "add_message":
        test_add_message(args.message, args.model)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
