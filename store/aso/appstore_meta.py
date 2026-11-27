"""App Store metadata for v1.4.5. name<=30, subtitle<=30, keywords<=100 (no spaces after commas,
no words already in name/subtitle). Promotional text <=170 can be changed anytime without review."""
M = {
 "en-US": dict(name="Fat Cat To Do List & Planner", subtitle="Daily reminders for cat lovers",
   keywords="todo,checklist,task,habit,tracker,calendar,widget,countdown,dday,cute,kawaii,kitty,organizer,agenda",
   promo="Finish your to-do list and watch Mochi the fat cat celebrate! Reminders that ring like an alarm, habit tracker, widgets & D-Day countdowns. Cute, private, no ads."),
 "ja": dict(name="Fat Cat ToDoリスト：猫のタスク管理", subtitle="かわいいリマインダーと習慣記録",
   keywords="やることリスト,スケジュール,カレンダー,チェックリスト,ウィジェット,カウントダウン,予定,メモ,ねこ,手帳,日記,勉強,習慣化,todo",
   promo="やることを終えると、太っちょ猫のMochiがお祝い！アラームのように鳴るリマインダー、習慣記録、ウィジェット、D-Dayカウントダウン。広告なし。"),
 "ko": dict(name="Fat Cat 투두리스트: 고양이 플래너", subtitle="귀여운 할 일 알림 & 습관 체크",
   keywords="todo,체크리스트,일정,캘린더,다이어리,디데이,위젯,메모,스케줄,루틴,공부,냥이,계획표,to do",
   promo="할 일을 끝내면 뚱냥이 Mochi가 함께 축하해요! 알람처럼 울리는 알림, 습관 체크, 위젯, 디데이 카운트다운. 광고 없음."),
 "zh-Hant": dict(name="Fat Cat 待辦清單：可愛貓咪計畫表", subtitle="提醒、習慣打卡、倒數日",
   keywords="todo,行事曆,日曆,備忘錄,手帳,檢查清單,小工具,日程,行程,規劃,任務,記事,讀書,喵,效率",
   promo="完成待辦，胖貓 Mochi 陪你一起慶祝！像鬧鐘一樣響的提醒、習慣打卡、桌面小工具、倒數日。無廣告。"),
 "zh-Hans": dict(name="Fat Cat 待办清单：可爱猫咪计划表", subtitle="提醒、习惯打卡、倒数日",
   keywords="todo,日历,备忘录,手账,检查清单,小组件,日程,行程,规划,任务,记事,学习,喵,效率",
   promo="完成待办，胖猫 Mochi 陪你一起庆祝！像闹钟一样响的提醒、习惯打卡、桌面小组件、倒数日。无广告。"),
 "de-DE": dict(name="Fat Cat To-Do-Liste & Planer", subtitle="Erinnerungen für Katzenfans",
   keywords="aufgaben,checkliste,kalender,gewohnheiten,tracker,widget,countdown,organizer,termine,süß,kawaii,todo",
   promo="Erledige deine To-dos und Mochi, die dicke Katze, feiert mit! Erinnerungen wie ein Wecker, Gewohnheiten, Widgets & Countdowns. Keine Werbung."),
 "fr-FR": dict(name="Fat Cat : To-Do List & Agenda", subtitle="Rappels pour fans de chats",
   keywords="tâches,checklist,calendrier,habitudes,widget,compte,rebours,organiseur,planning,mignon,kawaii,todo",
   promo="Terminez vos tâches et Mochi, le gros chat, fait la fête ! Rappels comme un réveil, habitudes, widgets et comptes à rebours. Sans pub."),
 "vi": dict(name="Fat Cat - Việc Cần Làm & Lịch", subtitle="Nhắc việc cho người yêu mèo",
   keywords="todo,to do,danh sách,nhắc nhở,thói quen,ghi chú,kế hoạch,checklist,widget,đếm ngược,dễ thương",
   promo="Làm xong việc, mèo béo Mochi ăn mừng cùng bạn! Nhắc việc reo như báo thức, theo dõi thói quen, widget, đếm ngược D-Day. Không quảng cáo."),
}
if __name__ == "__main__":
    for k, v in M.items():
        print(k, len(v["name"]), len(v["subtitle"]), len(v["keywords"]), len(v["keywords"].encode()), len(v["promo"]))
