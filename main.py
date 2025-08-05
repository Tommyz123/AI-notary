from teaching_controller import TeachingController
from deepseek_api import call_openai    
from progress import load_progress, save_progress

def load_prompt_template():
    with open("prompt_template.txt", "r", encoding="utf-8") as f:
        return f.read()

def choose_lesson(controller):
    while True:
        print("\n📘 操作菜单：")
        print("1️⃣ 输入数字 → 跳转到指定章节")
        print("2️⃣ 输入 c    → 继续上次进度")
        print("3️⃣ 输入 m    → 查看目录")
        print("4️⃣ 输入 q    → 退出系统")
        user_input = input("👉 请输入操作：").strip()

        if user_input == "q":
            exit()
        elif user_input == "m":
            controller.show_catalog()
        elif user_input == "c":
            index = load_progress()
            controller.set_index(index)
            return
        elif user_input.isdigit():
            controller.set_index(int(user_input) - 1)
            return
        else:
            print("⚠️ 无效输入，请重试。")

def check_command(controller):
    """
    在任何中断点检查用户输入命令。
    返回 False 表示继续当前流程，返回 True 表示重新跳转。
    """
    cmd = input("\n>>> 按 Enter 进入下一节，或输入 m（菜单）/ q（退出）/ 数字（跳转）：\n").strip()
    if cmd == "":
        return False
    elif cmd == "q":
        exit()
    elif cmd == "m":
        controller.show_catalog()
        choose_lesson(controller)
        return True
    elif cmd.isdigit():
        controller.set_index(int(cmd) - 1)
        return True
    else:
        print("⚠️ 无效输入，将继续当前流程。")
        return False

def main():
    controller = TeachingController("lessons.csv")
    prompt_template = load_prompt_template()

    choose_lesson(controller)  # 第一次进入主菜单

    while controller.has_next():
        lesson = controller.next_lesson()
        save_progress(controller.index)

        print(f"\n=== 正在讲解第 {lesson['id']} 课：{lesson['title']} ===\n")

        prompt = prompt_template.format(
            id=lesson["id"],
            title=lesson["title"],
            content=lesson["content"]
        )
        messages = [
            {"role": "system", "content": "你是一位经验丰富、善于教学的 AI 教师"},
            {"role": "user", "content": prompt}
        ]
        output = call_openai(messages)
        print(output)

        # ⏸️ 插入提问流程
        while True:
            question = input("\n💬 想提问这节内容吗？请输入问题（或输入 m 跳转 / q 退出 / Enter 跳过）：\n").strip()
            if question == "":
                break
            elif question == "q":
                exit()
            elif question == "m":
                controller.show_catalog()
                choose_lesson(controller)
                break
            elif question.isdigit():
                controller.set_index(int(question) - 1)
                break
            else:
                qa_prompt = f"""以下是课程内容：
{lesson['content']}

请根据以上内容回答学生提出的问题：
问题：{question}
"""
                messages_qa = [
                    {"role": "system", "content": "你是一个有耐心的教学助手"},
                    {"role": "user", "content": qa_prompt}
                ]
                answer = call_openai(messages_qa)
                print(f"\n📘 AI 回答：\n{answer}")

        # 🧭 节结束：是否跳转
        jumped = check_command(controller)
        if jumped:
            continue

if __name__ == "__main__":
    main()
