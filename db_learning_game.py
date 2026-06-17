import json
import os
import sqlite3
import datetime
import textwrap

DB_FILENAME = "db_learning_game.db"

LEVELS = [
    {"id": 1, "title": "SELECT Básico", "xp_needed": 100},
    {"id": 2, "title": "Filtrando com WHERE", "xp_needed": 200},
    {"id": 3, "title": "Ordenação e LIMIT", "xp_needed": 300},
    {"id": 4, "title": "JUNÇÕES", "xp_needed": 400},
    {"id": 5, "title": "Agrupamento e funções", "xp_needed": 500},
]

SEED_QUESTIONS = [
    {
        "level": 1,
        "topic": "SELECT",
        "text": "Qual comando SQL é usado para pegar colunas de uma tabela?",
        "options": ["INSERT", "SELECT", "UPDATE", "DELETE"],
        "answer": "SELECT",
        "explanation": "SELECT é usado para recuperar dados de colunas em uma tabela.",
    },
    {
        "level": 1,
        "topic": "SELECT",
        "text": "Qual cláusula seleciona todas as colunas de uma tabela?",
        "options": ["*", "ALL", "EVERY", "COLUMNS"],
        "answer": "*",
        "explanation": "O asterisco (*) seleciona todas as colunas de uma tabela.",
    },
    {
        "level": 2,
        "topic": "WHERE",
        "text": "Como você filtra registros onde a idade é maior que 18?",
        "options": ["WHERE idade > 18", "FILTER idade > 18", "HAVING idade > 18", "SELECT idade > 18"],
        "answer": "WHERE idade > 18",
        "explanation": "A cláusula WHERE é usada para filtrar linhas que atendem a uma condição.",
    },
    {
        "level": 2,
        "topic": "WHERE",
        "text": "Qual opção retorna apenas os produtos com estoque igual a zero?",
        "options": ["WHERE estoque = 0", "WHERE estoque LIKE 0", "WHERE estoque IS ZERO", "WHERE estoque < 0"],
        "answer": "WHERE estoque = 0",
        "explanation": "Uso correto da cláusula WHERE para igualdade numérica.",
    },
    {
        "level": 3,
        "topic": "Ordenação",
        "text": "Qual cláusula ordena resultados em ordem decrescente?",
        "options": ["ORDER BY ... DESC", "SORT BY ... DOWN", "ORDER BY ... ASC", "GROUP BY ... DESC"],
        "answer": "ORDER BY ... DESC",
        "explanation": "DESC ordena do maior para o menor.",
    },
    {
        "level": 3,
        "topic": "LIMIT",
        "text": "Como limitar a consulta aos 5 primeiros resultados?",
        "options": ["LIMIT 5", "TOP 5", "FIRST 5", "MAX 5"],
        "answer": "LIMIT 5",
        "explanation": "LIMIT define quantos registros retornar.",
    },
    {
        "level": 4,
        "topic": "JOIN",
        "text": "Qual tipo de JOIN retorna apenas registros que têm correspondência em ambas as tabelas?",
        "options": ["INNER JOIN", "LEFT JOIN", "RIGHT JOIN", "FULL JOIN"],
        "answer": "INNER JOIN",
        "explanation": "INNER JOIN retorna apenas as linhas que aparecem em ambas as tabelas.",
    },
    {
        "level": 4,
        "topic": "JOIN",
        "text": "Qual comando liga duas tabelas usando uma coluna comum?",
        "options": ["... JOIN ... ON ...", "... UNION ... ON ...", "... MERGE ... ON ...", "... CONNECT ... USING ..."],
        "answer": "... JOIN ... ON ...",
        "explanation": "JOIN com ON usa a condição de coluna comum para unir tabelas.",
    },
    {
        "level": 5,
        "topic": "GROUP BY",
        "text": "Qual cláusula agrupa resultados por uma coluna?",
        "options": ["GROUP BY", "ORDER BY", "PARTITION BY", "FILTER BY"],
        "answer": "GROUP BY",
        "explanation": "GROUP BY agrupa linhas para uso com funções agregadas.",
    },
    {
        "level": 5,
        "topic": "Funções agregadas",
        "text": "Qual função retorna a soma de um conjunto de valores?",
        "options": ["SUM", "COUNT", "MIN", "AVG"],
        "answer": "SUM",
        "explanation": "SUM soma valores numéricos em uma coluna.",
    },
]


def connect_db():
    return sqlite3.connect(DB_FILENAME)


def init_db():
    first_run = not os.path.exists(DB_FILENAME)
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            level INTEGER NOT NULL,
            xp INTEGER NOT NULL,
            gems INTEGER NOT NULL,
            streak INTEGER NOT NULL,
            last_session TEXT
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            level INTEGER NOT NULL,
            topic TEXT NOT NULL,
            text TEXT NOT NULL,
            options TEXT NOT NULL,
            answer TEXT NOT NULL,
            explanation TEXT NOT NULL
        )
        """
    )

    if first_run or cursor.execute("SELECT COUNT(*) FROM questions").fetchone()[0] == 0:
        for question in SEED_QUESTIONS:
            cursor.execute(
                "INSERT INTO questions (level, topic, text, options, answer, explanation) VALUES (?, ?, ?, ?, ?, ?)",
                (
                    question["level"],
                    question["topic"],
                    question["text"],
                    json.dumps(question["options"], ensure_ascii=False),
                    question["answer"],
                    question["explanation"],
                ),
            )

    conn.commit()
    conn.close()


def format_header(title):
    return f"\n{'=' * 60}\n{title}\n{'=' * 60}\n"


def load_user(username):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT username, level, xp, gems, streak, last_session FROM users WHERE username = ?", (username,))
    row = cursor.fetchone()
    conn.close()
    return row


def create_user(username):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT OR REPLACE INTO users (username, level, xp, gems, streak, last_session) VALUES (?, ?, ?, ?, ?, ?)",
        (username, 1, 0, 0, 0, None),
    )
    conn.commit()
    conn.close()
    return load_user(username)


def update_user(username, level=None, xp=None, gems=None, streak=None, last_session=None):
    user = load_user(username)
    if not user:
        return None

    new_level = level if level is not None else user[1]
    new_xp = xp if xp is not None else user[2]
    new_gems = gems if gems is not None else user[3]
    new_streak = streak if streak is not None else user[4]
    new_last_session = last_session if last_session is not None else user[5]

    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE users SET level = ?, xp = ?, gems = ?, streak = ?, last_session = ? WHERE username = ?",
        (new_level, new_xp, new_gems, new_streak, new_last_session, username),
    )
    conn.commit()
    conn.close()
    return load_user(username)


def get_level_info(level_id):
    return next((level for level in LEVELS if level["id"] == level_id), None)


def compute_level_progress(xp, level):
    current_level_info = get_level_info(level)
    next_level_info = get_level_info(level + 1)
    if not next_level_info:
        return 100
    required = current_level_info["xp_needed"]
    return min(100, int((xp / required) * 100))


def award_xp_and_gems(username, earned_xp, earned_gems=0):
    user = load_user(username)
    if not user:
        return
    level, xp, gems = user[1], user[2], user[3]
    xp += earned_xp
    gems += earned_gems

    current_level_info = get_level_info(level)
    while current_level_info and xp >= current_level_info["xp_needed"]:
        xp -= current_level_info["xp_needed"]
        level += 1
        current_level_info = get_level_info(level)
        print(f"Parabéns! Você desbloqueou a fase {level}.")

    update_user(username, level=level, xp=xp, gems=gems)


def update_streak(username):
    user = load_user(username)
    if not user:
        return
    last_session = user[5]
    today = datetime.date.today()
    streak = user[4]

    if last_session:
        last_date = datetime.datetime.strptime(last_session, "%Y-%m-%d").date()
        if last_date == today:
            return streak
        if last_date == today - datetime.timedelta(days=1):
            streak += 1
            if streak % 3 == 0:
                award_xp_and_gems(username, earned_xp=20, earned_gems=1)
                print("Bônus de streak! Você ganhou 20 XP e 1 gema.")
        else:
            streak = 1
    else:
        streak = 1

    update_user(username, streak=streak, last_session=today.isoformat())
    return streak


def show_user_dashboard(user):
    level_info = get_level_info(user[1])
    progress = compute_level_progress(user[2], user[1])

    print(format_header(f"Painel de {user[0]}"))
    print(f"Fase atual: {level_info['id']} - {level_info['title']}")
    print(f"XP: {user[2]} / {level_info['xp_needed']}")
    print(f"Progresso na fase: {progress}%")
    print(f"Gemas: {user[3]}")
    print(f"Sequência de estudos: {user[4]} dia(s)")
    print("Use o menu para continuar ou repetir uma fase.")


def choose_level():
    print(format_header("Fases Disponíveis"))
    for level in LEVELS:
        print(f"{level['id']}. {level['title']} (XP necessário: {level['xp_needed']})")
    while True:
        escolha = input("Escolha uma fase (número) ou ENTER para voltar: ").strip()
        if escolha == "":
            return None
        if escolha.isdigit() and int(escolha) in [level["id"] for level in LEVELS]:
            return int(escolha)
        print("Entrada inválida. Digite um número de fase válido.")


def choose_questions(level_id):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT text, options, answer, explanation FROM questions WHERE level = ?", (level_id,))
    rows = cursor.fetchall()
    conn.close()
    questions = []
    for row in rows:
        questions.append(
            {
                "text": row[0],
                "options": json.loads(row[1]),
                "answer": row[2],
                "explanation": row[3],
            }
        )
    return questions


def ask_questions(username, level_id):
    questions = choose_questions(level_id)
    if not questions:
        print("Ainda não há perguntas para essa fase.")
        return

    print(format_header(f"Fase {level_id}: {get_level_info(level_id)['title']}"))
    correct = 0
    for idx, question in enumerate(questions, start=1):
        print(f"\nQuestão {idx}/{len(questions)}")
        print(textwrap.fill(question["text"], width=70))
        for option_index, option in enumerate(question["options"], start=1):
            print(f"  {option_index}. {option}")

        answer = input("Digite o número da resposta correta: ").strip()
        if not answer.isdigit() or not (1 <= int(answer) <= len(question["options"])):
            print("Resposta inválida. Vamos considerar como incorreta.")
            print(f"Explicação: {question['explanation']}")
            continue

        selected = question["options"][int(answer) - 1]
        if selected == question["answer"]:
            correct += 1
            print("Correto! Você ganhou 20 XP.")
            award_xp_and_gems(username, earned_xp=20)
        else:
            print(f"Incorreto. Resposta certa: {question['answer']}")
            print(f"Explicação: {question['explanation']}")

    print(format_header("Resultado da Fase"))
    print(f"Você acertou {correct} de {len(questions)} perguntas.")
    if correct == len(questions):
        print("Excelente! Bônus de fase concluída: 10 gemas.")
        award_xp_and_gems(username, earned_xp=30, earned_gems=10)
    elif correct >= len(questions) // 2:
        print("Bom trabalho! Continue praticando para completar a fase.")
        award_xp_and_gems(username, earned_xp=10)
    else:
        print("Não desanime! Revise a fase e tente novamente.")


def main():
    init_db()
    print(format_header("Aprenda Banco de Dados com Gamificação"))
    print("Bem-vindo ao app de aprendizado estilo Duolingo para SQL.")
    username = input("Digite seu nome de jogador: ").strip()
    if not username:
        print("Nome inválido. Reinicie o app e insira um nome válido.")
        return

    if not load_user(username):
        create_user(username)
        print(f"Olá, {username}! Seu perfil foi criado.")
    else:
        print(f"Bem-vindo de volta, {username}!")

    streak = update_streak(username)
    if streak:
        print(f"Sua sequência de estudos está em {streak} dia(s).")

    while True:
        user = load_user(username)
        show_user_dashboard(user)

        print("\nMenu:")
        print("1. Jogar fase atual")
        print("2. Escolher outra fase")
        print("3. Ver dicas rápidas de SQL")
        print("4. Sair")
        choice = input("Escolha uma opção: ").strip()

        if choice == "1":
            ask_questions(username, user[1])
        elif choice == "2":
            chosen = choose_level()
            if chosen:
                ask_questions(username, chosen)
        elif choice == "3":
            show_tips()
        elif choice == "4":
            print("Até a próxima! Continue praticando SQL.")
            break
        else:
            print("Opção inválida. Tente novamente.")


def show_tips():
    tips = [
        "SELECT escolhe dados; sempre comece pela tabela correta.",
        "WHERE filtra resultados; use operadores como =, >, <, >=, <=.",
        "ORDER BY organiza resultados; use ASC ou DESC.",
        "JOIN combina tabelas relacionadas; INNER JOIN é o mais comum.",
        "GROUP BY agrupa resultados para funções agregadas como SUM e AVG.",
    ]
    print(format_header("Dicas Rápidas de SQL"))
    for tip in tips:
        print(f"- {tip}")
    input("Pressione ENTER para voltar ao menu.")


if __name__ == "__main__":
    main()
