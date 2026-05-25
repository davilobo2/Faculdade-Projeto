import flet as ft
import ssl
import random
import json
import os

ssl._create_default_https_context = ssl._create_unverified_context

# --- CONFIGURAÇÃO DO ARQUIVO DE BANCO DE DADOS ---
ARQUIVO_DADOS = "banco_geriatria.json"

# --- VARIÁVEIS GLOBAIS DE MEMÓRIA ---
pacientes_gds = []
pacientes_facit = []
pacientes_whosrpb = []


# --- LÓGICAS DE CLASSIFICAÇÃO ---
def classificar_gds15(escore):
    if escore <= 5:
        return ("Normal", "green", "Reavaliação anual.")
    elif escore <= 9:
        return ("Leve", "amber", "Avaliação e acompanhamento clínico.")
    elif escore <= 12:
        return ("Moderada", "orange", "Intervenção terapêutica indicada.")
    else:
        return ("Grave", "red", "Urgência Psiquiátrica.")


def classificar_facit(escore):
    if escore <= 12:
        return "Baixo"
    elif escore <= 24:
        return "Médio"
    else:
        return "Alto"


def classificar_whosrpb(escore):
    if escore >= 120:
        return ("Alta Resiliência", "green", "Forte suporte interno.")
    elif 80 <= escore < 120:
        return ("Resiliência Moderada", "blue", "Suporte interno mediano.")
    else:
        return ("Baixa Resiliência", "red", "Risco alto se GDS elevada.")


# --- DADOS DOS TESTES ---
questoes_gds = [
    ("1. Você está satisfeito com sua vida?", 0),
    ("2. Você interrompeu muitas de suas atividades?", 1),
    ("3. Você sente que sua vida está vazia?", 1),
    ("4. Você se sente aborrecido(a) com frequência?", 1),
    ("5. Você sente-se de bom humor a maior parte do tempo?", 0),
    ("6. Você tem medo que algo ruim lhe aconteça?", 1),
    ("7. Você se sente feliz a maior parte do tempo?", 0),
    ("8. Você se sente desamparado(a) com frequência?", 1),
    ("9. Você prefere ficar em casa a sair?", 1),
    ("10. Você sente que tem mais problemas que as outras pessoas?", 1),
    ("11. Você acha que é maravilhoso estar vivo(a)?", 0),
    ("12. Você se sente inútil no estado em que se encontra?", 1),
    ("13. Você se sente cheio(a) de energia?", 0),
    ("14. Você sente que sua situação é sem esperança?", 1),
    ("15. Você acha que os outros tem mais sorte que você?", 1)
]

questoes_facit = [
    ("Sp1: Sinto-me em paz.", False), ("Sp2: Tenho uma razão para viver.", False),
    ("Sp3: Custa-me sentir paz de espírito.", True), ("Sp4: Sinto que a minha vida tem um propósito.", False),
    ("Sp5: Sou capaz de encontrar conforto dentro de mim.", False),
    ("Sp6: Sinto-me em harmonia comigo mesmo(a).", False),
    ("Sp7: Falta sentido e propósito na minha vida.", True), ("Sp8: Encontro conforto na minha fé/crenças.", False),
    ("Sp9: Minha fé/crenças dão-me força.", False)
]

dominios_whosrpb = [
    ("1. Conexão a ser ou força espiritual", [
        "1.1 Até que ponto alguma ligação a um ser espiritual ajuda você a passar por épocas difíceis?",
        "1.2 Até que ponto alguma ligação com um ser espiritual ajuda você a tolerar o estresse?",
        "1.3 Até que ponto alguma ligação com um ser espiritual ajuda você a compreender os outros?",
        "1.4 Até que ponto alguma ligação com um ser espiritual conforta/tranquiliza você?"
    ]),
    ("2. Sentido na vida", [
        "2.1 Até que ponto você encontra um sentido na vida?",
        "2.2 Até que ponto cuidar de outras pessoas proporciona um sentido na vida para você?",
        "2.3 Até que ponto você sente que a sua vida tem uma finalidade?",
        "2.4 Até que ponto você sente que está aqui por um motivo?"
    ]),
    ("3. Admiração", [
        "3.1 Até que ponto você consegue ter admiração pelas coisas a seu redor? (ex: natureza, arte, música)",
        "3.2 Até que ponto você se sente espiritualmente tocado pela beleza?",
        "3.3 Até que ponto você tem sentimentos de inspiração (emoção) na sua vida?",
        "3.4 Até que ponto você se sente agradecido por poder apreciar ('curtir') as coisas da natureza?"
    ]),
    ("4. Totalidade & Integração", [
        "4.1 Até que ponto você sente alguma ligação entre a sua mente, corpo e alma?",
        "4.2 Quão satisfeito você está por ter um equilíbrio entre a mente, o corpo e a alma?",
        "4.3 Até que ponto você sente que a maneira em que vive está de acordo com o que você sente e pensa?",
        "4.4 Quanto as suas crenças ajudam-no a criar uma coerência (harmonia) entre o que você faz, pensa e sente?"

    ]),
    ("5. Força espiritual", [
        "5.1 Até que ponto você sente força espiritual interior?",
        "5.2 Até que ponto você pode encontrar força espiritual em épocas difíceis?",
        "5.3 Quanto a força espiritual o ajuda a viver melhor?",
        "5.4 Até que ponto a sua força espiritual o ajuda a se sentir feliz na vida?"
    ]),
    ("6. Paz interior", [
        "6.1 Até que ponto você se sente em paz consigo mesmo?",
        "6.2 Até que ponto você tem paz interior?",
        "6.3 Quanto você consegue sentir paz quando você necessita disso?",
        "6.4 Até que ponto você sente um senso de harmonia na sua vida?"
    ]),
    ("7. Esperança e otimismo", [
        "7.1 Quão esperançoso você se sente?",
        "7.2 Até que ponto você está esperançoso com a sua vida?",
        "7.3 Até que ponto ser otimista melhora a sua qualidade de vida?",
        "7.4 Quanto você é capaz de permanecer otimista em épocas de incerteza?"
    ]),
    ("8. Fé", [
        "8.1 Até que ponto a fé contribui para o seu bem-estar?",
        "8.2 Até que ponto a fé lhe dá conforto no dia-a-dia?",
        "8.3 Até que ponto a fé lhe dá força no dia-a-dia?",
        "8.4 Até que ponto a fé o ajuda a aproveitar a vida?"
    ])
]


def main(page: ft.Page):
    page.title = "Geriatria Pro - RU: 4299010"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.window_width = 700
    page.window_height = 800
    page.padding = 20
    page.scroll = "auto"

    global pacientes_gds, pacientes_facit, pacientes_whosrpb

    # --- FUNÇÃO PARA ALERTA DE ERRO ---
    def mostrar_alerta_preenchimento():
        snack = ft.SnackBar(content=ft.Text(
            "⚠️ Atenção: Preencha todos os dados do paciente e todas as perguntas. Se o paciente não respondeu, selecione a opção 'Pular'."),
                            bgcolor="red")
        page.overlay.append(snack)
        snack.open = True
        page.update()

    # --- FUNÇÕES DO ARQUIVO JSON (SALVAR E CARREGAR) ---
    def carregar_dados():
        if os.path.exists(ARQUIVO_DADOS):
            try:
                with open(ARQUIVO_DADOS, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        return {"gds": [], "facit": [], "whosrpb": [], "lembretes": {"inst": "", "resp": "", "est": ""}}

    banco = carregar_dados()
    pacientes_gds.clear();
    pacientes_gds.extend(banco["gds"])
    pacientes_facit.clear();
    pacientes_facit.extend(banco["facit"])
    pacientes_whosrpb.clear();
    pacientes_whosrpb.extend(banco["whosrpb"])

    estado_memoria = {
        "inst": banco["lembretes"]["inst"], "lembrar_inst": True,
        "resp": banco["lembretes"]["resp"], "lembrar_resp": True,
        "est": banco["lembretes"]["est"], "lembrar_est": True,
        "modo_dev": False
    }

    def salvar_dados():
        dados = {
            "gds": pacientes_gds,
            "facit": pacientes_facit,
            "whosrpb": pacientes_whosrpb,
            "lembretes": {
                "inst": estado_memoria["inst"] if estado_memoria["lembrar_inst"] else "",
                "resp": estado_memoria["resp"] if estado_memoria["lembrar_resp"] else "",
                "est": estado_memoria["est"] if estado_memoria["lembrar_est"] else ""
            }
        }
        with open(ARQUIVO_DADOS, 'w', encoding='utf-8') as f:
            json.dump(dados, f, ensure_ascii=False, indent=4)

    def ir_para_home(e=None):
        page.clean()
        page.add(renderizar_home())
        page.update()

    # --- TELA GDS-15 ---
    def abrir_gds(e):
        page.clean()

        if estado_memoria["modo_dev"]:
            respostas_gds = [random.choice([0, 1, -1]) for _ in range(15)]  # -1 é o valor secreto para "Pular"
        else:
            respostas_gds = [None] * 15

        campo_nome = ft.TextField(label="Nome do Paciente", border_radius=10, expand=True)
        campo_sexo = ft.Dropdown(label="Sexo",
                                 options=[ft.dropdown.Option("Feminino"), ft.dropdown.Option("Masculino")], width=150)
        linha_paciente = ft.Row([campo_nome, campo_sexo], width=400)

        if estado_memoria["modo_dev"]:
            campo_sexo.value = random.choice(["Feminino", "Masculino"])

        campo_inst = ft.TextField(label="Instituição (Ex: Asilo 1)", border_radius=10, value=estado_memoria["inst"],
                                  width=400)
        check_inst = ft.Checkbox(label="Lembrar", value=estado_memoria["lembrar_inst"])
        campo_resp = ft.TextField(label="Nome do Responsável", border_radius=10, value=estado_memoria["resp"],
                                  width=400)
        check_resp = ft.Checkbox(label="Lembrar", value=estado_memoria["lembrar_resp"])
        campo_est = ft.TextField(label="Nome do Estudante", border_radius=10, value=estado_memoria["est"], width=400)
        check_est = ft.Checkbox(label="Lembrar", value=estado_memoria["lembrar_est"])

        lista_perguntas = ft.Column(scroll="always", expand=True)
        view_hist = ft.Column(scroll="always", expand=True, visible=False)
        view_fichas = ft.Column(scroll="always", expand=True, visible=False)

        btn_aba_ficha = ft.ElevatedButton("Nova Ficha", bgcolor="blue", color="white",
                                          on_click=lambda _: alternar("nova"))
        btn_aba_hist = ft.ElevatedButton("Histórico", bgcolor="grey300", color="black",
                                         on_click=lambda _: alternar("hist"))
        btn_aba_fichas_det = ft.ElevatedButton("Fichas Completas", bgcolor="grey300", color="black",
                                               on_click=lambda _: alternar("fichas"))

        def alternar(aba):
            view_ficha.visible = (aba == "nova")
            view_hist.visible = (aba == "hist")
            view_fichas.visible = (aba == "fichas")

            for btn in [btn_aba_ficha, btn_aba_hist, btn_aba_fichas_det]:
                btn.bgcolor = "grey300";
                btn.color = "black"

            if aba == "nova":
                btn_aba_ficha.bgcolor = "blue";
                btn_aba_ficha.color = "white"
            elif aba == "hist":
                btn_aba_hist.bgcolor = "blue";
                btn_aba_hist.color = "white"
                atualizar_historico()
            elif aba == "fichas":
                btn_aba_fichas_det.bgcolor = "blue";
                btn_aba_fichas_det.color = "white"
                atualizar_fichas_detalhadas()
            page.update()

        def render_perguntas():
            lista_perguntas.controls.clear()
            if estado_memoria["modo_dev"]:
                lista_perguntas.controls.append(
                    ft.Text("⚠️ MODO DEV ATIVO: Respostas preenchidas aleatoriamente", color="red", weight="bold"))

            lista_perguntas.controls.append(linha_paciente)
            lista_perguntas.controls.append(ft.Row([campo_inst, check_inst]))
            lista_perguntas.controls.append(ft.Row([campo_resp, check_resp]))
            lista_perguntas.controls.append(ft.Row([campo_est, check_est]))
            lista_perguntas.controls.append(ft.Divider())

            for i, (txt, _) in enumerate(questoes_gds):
                cor_s = "blue200" if respostas_gds[i] == 1 else "grey100"
                cor_n = "blue200" if respostas_gds[i] == 0 else "grey100"
                cor_p = "grey500" if respostas_gds[i] == -1 else "grey100"  # Cor para o botão Pular

                def sel(idx, v):
                    def ck(e): respostas_gds[idx] = v; render_perguntas(); page.update()

                    return ck

                lista_perguntas.controls.append(ft.Column([
                    ft.Text(txt, weight="bold"),
                    ft.Row([
                        ft.ElevatedButton("SIM", bgcolor=cor_s, on_click=sel(i, 1)),
                        ft.ElevatedButton("NÃO", bgcolor=cor_n, on_click=sel(i, 0)),
                        ft.ElevatedButton("PULAR", bgcolor=cor_p, on_click=sel(i, -1))  # BOTÃO PULAR ADICIONADO
                    ])
                ]))

        def salvar_gds(e):
            # A TRAVA VOLTOU: O aluno é OBRIGADO a marcar pelo menos o "Pular" (-1). Se tiver None (em branco), trava.
            if None in respostas_gds or not campo_nome.value or not campo_inst.value or not campo_sexo.value:
                mostrar_alerta_preenchimento()
                return

            estado_memoria["lembrar_inst"] = check_inst.value
            estado_memoria["lembrar_resp"] = check_resp.value
            estado_memoria["lembrar_est"] = check_est.value
            estado_memoria["inst"] = campo_inst.value if check_inst.value else ""
            estado_memoria["resp"] = campo_resp.value if check_resp.value else ""
            estado_memoria["est"] = campo_est.value if check_est.value else ""

            escore = sum(1 for i, (_, alvo) in enumerate(questoes_gds) if respostas_gds[i] == alvo)
            pacientes_gds.append({
                "nome": campo_nome.value, "sexo": campo_sexo.value, "instituicao": campo_inst.value,
                "responsavel": campo_resp.value, "estudante": campo_est.value,
                "escore": escore, "respostas": respostas_gds.copy()
            })
            salvar_dados()
            ir_para_home()

        def atualizar_historico():
            view_hist.controls.clear()
            for i, p in enumerate(pacientes_gds):
                classe_dinamica, cor_dinamica, conduta_dinamica = classificar_gds15(p['escore'])
                view_hist.controls.append(ft.Container(
                    padding=15, border=ft.border.all(1, cor_dinamica), border_radius=10,
                    margin=ft.margin.only(bottom=10),
                    content=ft.Column([
                        ft.Row([
                            ft.Text(f"Paciente: {p['nome']} ({p.get('sexo', 'N/I')})", weight="bold", size=16,
                                    expand=True),
                            ft.ElevatedButton("X", bgcolor="red", color="white",
                                              on_click=lambda _, idx=i: [pacientes_gds.pop(idx), salvar_dados(),
                                                                         atualizar_historico(), page.update()])
                        ]),
                        ft.Text(f"Asilo/Inst.: {p['instituicao']}", size=14),
                        ft.Text(f"Responsável: {p['responsavel']} | Estudante: {p['estudante']}", size=12,
                                color="grey"),
                        ft.Text(f"Escore: {p['escore']} pts - {classe_dinamica}", color=cor_dinamica, weight="bold",
                                size=14),
                        ft.Text(f"Conduta: {conduta_dinamica}", size=13)
                    ], spacing=5)
                ))

        def atualizar_fichas_detalhadas():
            view_fichas.controls.clear()
            if not pacientes_gds:
                view_fichas.controls.append(ft.Text("Nenhum paciente cadastrado.", color="grey"))
                return

            for p in pacientes_gds:
                coluna_respostas = ft.Column(spacing=2)
                resps = p.get("respostas", [])

                if not resps:
                    coluna_respostas.controls.append(
                        ft.Text("⚠️ Respostas detalhadas não registradas nas versões anteriores do aplicativo.",
                                color="red", size=12))
                else:
                    for i, (txt, _) in enumerate(questoes_gds):
                        if resps[i] == 1:
                            resposta_texto = "SIM"
                        elif resps[i] == 0:
                            resposta_texto = "NÃO"
                        elif resps[i] == -1:
                            resposta_texto = "Não Respondeu (Pulo)"
                        else:
                            resposta_texto = "Erro/Em Branco"

                        coluna_respostas.controls.append(ft.Text(f"{txt} ➔ {resposta_texto}", size=12, color="grey800"))

                view_fichas.controls.append(ft.Container(
                    padding=15, border=ft.border.all(1, "grey400"), border_radius=10, margin=ft.margin.only(bottom=15),
                    bgcolor="grey50",
                    content=ft.Column([
                        ft.Text(f"📝 Ficha Detalhada: {p['nome']} ({p.get('sexo', 'N/I')})", weight="bold", size=16,
                                color="blue"),
                        ft.Text(f"Asilo: {p['instituicao']} | Escore Total: {p['escore']} pts", size=13, weight="bold"),
                        ft.Divider(),
                        coluna_respostas
                    ])
                ))

        render_perguntas()
        view_ficha = ft.Column([
            lista_perguntas,
            ft.ElevatedButton("SALVAR GDS", bgcolor="green", color="white", height=50, width=1000, on_click=salvar_gds)
        ], expand=True)

        page.add(ft.Column([
            ft.Row([ft.ElevatedButton("< MENU", on_click=ir_para_home),
                    ft.Text("GDS-15", size=20, weight="bold", color="blue")]),
            ft.Row([btn_aba_ficha, btn_aba_hist, btn_aba_fichas_det], alignment="center"),
            ft.Divider(), view_ficha, view_hist, view_fichas
        ], expand=True))

    # --- TELA FACIT-Sp-9 ---
    def abrir_facit(e):
        page.clean()

        if estado_memoria["modo_dev"]:
            respostas_facit = [random.choice([0, 1, 2, 3, 4, -1]) for _ in range(9)]
        else:
            respostas_facit = [None] * 9

        campo_nome = ft.TextField(label="Nome do Paciente", border_radius=10, expand=True)
        campo_sexo = ft.Dropdown(label="Sexo",
                                 options=[ft.dropdown.Option("Feminino"), ft.dropdown.Option("Masculino")], width=150)
        linha_paciente = ft.Row([campo_nome, campo_sexo], width=400)

        if estado_memoria["modo_dev"]:
            campo_sexo.value = random.choice(["Feminino", "Masculino"])

        campo_inst = ft.TextField(label="Instituição (Ex: Asilo 1)", border_radius=10, value=estado_memoria["inst"],
                                  width=400)
        check_inst = ft.Checkbox(label="Lembrar", value=estado_memoria["lembrar_inst"])
        campo_resp = ft.TextField(label="Nome do Responsável", border_radius=10, value=estado_memoria["resp"],
                                  width=400)
        check_resp = ft.Checkbox(label="Lembrar", value=estado_memoria["lembrar_resp"])
        campo_est = ft.TextField(label="Nome do Estudante", border_radius=10, value=estado_memoria["est"], width=400)
        check_est = ft.Checkbox(label="Lembrar", value=estado_memoria["lembrar_est"])

        lista_perguntas = ft.Column(scroll="always", expand=True)
        view_hist = ft.Column(scroll="always", expand=True, visible=False)
        view_fichas = ft.Column(scroll="always", expand=True, visible=False)

        btn_f = ft.ElevatedButton("Nova Ficha", bgcolor="purple", color="white", on_click=lambda _: alternar("nova"))
        btn_h = ft.ElevatedButton("Histórico", bgcolor="grey300", color="black", on_click=lambda _: alternar("hist"))
        btn_det = ft.ElevatedButton("Fichas Completas", bgcolor="grey300", color="black",
                                    on_click=lambda _: alternar("fichas"))

        def alternar(aba):
            view_ficha.visible = (aba == "nova")
            view_hist.visible = (aba == "hist")
            view_fichas.visible = (aba == "fichas")

            for btn in [btn_f, btn_h, btn_det]:
                btn.bgcolor = "grey300";
                btn.color = "black"

            if aba == "nova":
                btn_f.bgcolor = "purple";
                btn_f.color = "white"
            elif aba == "hist":
                btn_h.bgcolor = "purple";
                btn_h.color = "white"
                atualizar_hist()
            elif aba == "fichas":
                btn_det.bgcolor = "purple";
                btn_det.color = "white"
                atualizar_fichas_detalhadas()
            page.update()

        def render_perguntas():
            lista_perguntas.controls.clear()
            if estado_memoria["modo_dev"]:
                lista_perguntas.controls.append(
                    ft.Text("⚠️ MODO DEV ATIVO: Respostas preenchidas aleatoriamente", color="red", weight="bold"))

            lista_perguntas.controls.append(linha_paciente)
            lista_perguntas.controls.append(ft.Row([campo_inst, check_inst]))
            lista_perguntas.controls.append(ft.Row([campo_resp, check_resp]))
            lista_perguntas.controls.append(ft.Row([campo_est, check_est]))
            lista_perguntas.controls.append(
                ft.Text("Escala: 0=Nada | 1=Pouco | 2=Médio | 3=Bastante | 4=Muitíssimo | Pular", size=12, italic=True))
            lista_perguntas.controls.append(ft.Divider())

            for i, (q, _) in enumerate(questoes_facit):
                def mudar(idx):
                    def fn(e): respostas_facit[idx] = int(e.control.value)

                    return fn

                valor_inicial = str(respostas_facit[i]) if respostas_facit[i] is not None else None

                lista_perguntas.controls.append(ft.Column([
                    ft.Text(q, weight="bold"),
                    ft.RadioGroup(
                        value=valor_inicial,
                        content=ft.Row([
                            ft.Radio(value="0", label="0"), ft.Radio(value="1", label="1"),
                            ft.Radio(value="2", label="2"), ft.Radio(value="3", label="3"),
                            ft.Radio(value="4", label="4"), ft.Radio(value="-1", label="Pular")
                            # RADIO PULAR ADICIONADO
                        ]),
                        on_change=mudar(i)
                    ),
                    ft.Divider()
                ]))

        def salvar_facit(e):
            # A TRAVA VOLTOU
            if None in respostas_facit or not campo_nome.value or not campo_inst.value or not campo_sexo.value:
                mostrar_alerta_preenchimento()
                return

            estado_memoria["lembrar_inst"] = check_inst.value;
            estado_memoria["inst"] = campo_inst.value if check_inst.value else ""
            estado_memoria["lembrar_resp"] = check_resp.value;
            estado_memoria["resp"] = campo_resp.value if check_resp.value else ""
            estado_memoria["lembrar_est"] = check_est.value;
            estado_memoria["est"] = campo_est.value if check_est.value else ""

            # Cálculo Seguro: Ignora quem marcou "Pular" (-1)
            escore = sum((4 - v) if questoes_facit[i][1] else v for i, v in enumerate(respostas_facit) if v != -1)
            pacientes_facit.append({
                "nome": campo_nome.value, "sexo": campo_sexo.value, "instituicao": campo_inst.value,
                "responsavel": campo_resp.value, "estudante": campo_est.value, "escore": escore,
                "respostas": respostas_facit.copy()
            })
            salvar_dados()
            ir_para_home()

        def atualizar_hist():
            view_hist.controls.clear()
            for i, p in enumerate(pacientes_facit):
                view_hist.controls.append(ft.Container(
                    padding=15, border=ft.border.all(1, "purple"), border_radius=10, margin=ft.margin.only(bottom=10),
                    content=ft.Column([
                        ft.Row([
                            ft.Text(f"Paciente: {p['nome']} ({p.get('sexo', 'N/I')})", weight="bold", size=16,
                                    expand=True),
                            ft.ElevatedButton("X", bgcolor="red", color="white",
                                              on_click=lambda _, idx=i: [pacientes_facit.pop(idx), salvar_dados(),
                                                                         atualizar_hist(), page.update()])
                        ]),
                        ft.Text(f"Asilo/Inst.: {p['instituicao']}", size=14),
                        ft.Text(f"Responsável: {p['responsavel']} | Estudante: {p['estudante']}", size=12,
                                color="grey"),
                        ft.Text(f"Escore Espiritual: {p['escore']} / 36 pts", color="purple", weight="bold", size=14)
                    ], spacing=5)
                ))

        def atualizar_fichas_detalhadas():
            view_fichas.controls.clear()
            if not pacientes_facit:
                view_fichas.controls.append(ft.Text("Nenhum paciente cadastrado.", color="grey"))
                return

            escala_texto = {0: "0 (Nada)", 1: "1 (Pouco)", 2: "2 (Médio)", 3: "3 (Bastante)", 4: "4 (Muitíssimo)",
                            -1: "Não Respondeu (Pulo)", None: "Em Branco"}

            for p in pacientes_facit:
                coluna_respostas = ft.Column(spacing=2)
                resps = p.get("respostas", [])

                if not resps:
                    coluna_respostas.controls.append(
                        ft.Text("⚠️ Respostas detalhadas não registradas nas versões anteriores.", color="red",
                                size=12))
                else:
                    for i, (txt, _) in enumerate(questoes_facit):
                        resp_num = resps[i]
                        coluna_respostas.controls.append(
                            ft.Text(f"{txt} ➔ {escala_texto.get(resp_num, 'Erro')}", size=12, color="grey800"))

                view_fichas.controls.append(ft.Container(
                    padding=15, border=ft.border.all(1, "grey400"), border_radius=10, margin=ft.margin.only(bottom=15),
                    bgcolor="grey50",
                    content=ft.Column([
                        ft.Text(f"📝 Ficha Detalhada: {p['nome']} ({p.get('sexo', 'N/I')})", weight="bold", size=16,
                                color="purple"),
                        ft.Text(f"Asilo: {p['instituicao']} | Escore Total: {p['escore']} pts", size=13, weight="bold"),
                        ft.Divider(),
                        coluna_respostas
                    ])
                ))

        render_perguntas()
        view_ficha = ft.Column([
            lista_perguntas,
            ft.ElevatedButton("SALVAR FACIT", bgcolor="purple", color="white", height=50, width=1000,
                              on_click=salvar_facit)
        ], expand=True)

        page.add(ft.Column([
            ft.Row([ft.ElevatedButton("< MENU", on_click=ir_para_home),
                    ft.Text("FACIT-Sp-9", size=20, weight="bold", color="purple")]),
            ft.Row([btn_f, btn_h, btn_det], alignment="center"),
            ft.Divider(), view_ficha, view_hist, view_fichas
        ], expand=True))

    # --- TELA WHO-SRPB ---
    def abrir_whosrpb(e):
        page.clean()

        if estado_memoria["modo_dev"]:
            respostas_whosrpb = [random.randint(1, 5) if random.random() > 0.1 else -1 for _ in range(32)]
        else:
            respostas_whosrpb = [None] * 32

        campo_nome = ft.TextField(label="Nome do Paciente", border_radius=10, expand=True)
        campo_sexo = ft.Dropdown(label="Sexo",
                                 options=[ft.dropdown.Option("Feminino"), ft.dropdown.Option("Masculino")], width=150)
        linha_paciente = ft.Row([campo_nome, campo_sexo], width=400)

        if estado_memoria["modo_dev"]:
            campo_sexo.value = random.choice(["Feminino", "Masculino"])

        campo_inst = ft.TextField(label="Instituição (Ex: Asilo 1)", border_radius=10, value=estado_memoria["inst"],
                                  width=400)
        check_inst = ft.Checkbox(label="Lembrar", value=estado_memoria["lembrar_inst"])
        campo_resp = ft.TextField(label="Nome do Responsável", border_radius=10, value=estado_memoria["resp"],
                                  width=400)
        check_resp = ft.Checkbox(label="Lembrar", value=estado_memoria["lembrar_resp"])
        campo_est = ft.TextField(label="Nome do Estudante", border_radius=10, value=estado_memoria["est"], width=400)
        check_est = ft.Checkbox(label="Lembrar", value=estado_memoria["lembrar_est"])

        lista_perguntas = ft.Column(scroll="always", expand=True)
        view_hist = ft.Column(scroll="always", expand=True, visible=False)
        view_fichas = ft.Column(scroll="always", expand=True, visible=False)

        btn_f = ft.ElevatedButton("Nova Ficha", bgcolor="teal", color="white", on_click=lambda _: alternar("nova"))
        btn_h = ft.ElevatedButton("Histórico", bgcolor="grey300", color="black", on_click=lambda _: alternar("hist"))
        btn_det = ft.ElevatedButton("Fichas Completas", bgcolor="grey300", color="black",
                                    on_click=lambda _: alternar("fichas"))

        def alternar(show):
            view_ficha.visible = (show == "nova")
            view_hist.visible = (show == "hist")
            view_fichas.visible = (show == "fichas")

            for btn in [btn_f, btn_h, btn_det]:
                btn.bgcolor = "grey300";
                btn.color = "black"

            if show == "nova":
                btn_f.bgcolor = "teal";
                btn_f.color = "white"
            elif show == "hist":
                btn_h.bgcolor = "teal";
                btn_h.color = "white"
                atualizar_hist()
            elif show == "fichas":
                btn_det.bgcolor = "teal";
                btn_det.color = "white"
                atualizar_fichas_detalhadas()
            page.update()

        def render_perguntas():
            lista_perguntas.controls.clear()
            if estado_memoria["modo_dev"]:
                lista_perguntas.controls.append(
                    ft.Text("⚠️ MODO DEV ATIVO: Respostas preenchidas aleatoriamente", color="red", weight="bold"))

            lista_perguntas.controls.append(linha_paciente)
            lista_perguntas.controls.append(ft.Row([campo_inst, check_inst]))
            lista_perguntas.controls.append(ft.Row([campo_resp, check_resp]))
            lista_perguntas.controls.append(ft.Row([campo_est, check_est]))
            lista_perguntas.controls.append(
                ft.Text("Escala: 1=Nada | 2=Pouco | 3=Médio | 4=Muito | 5=Extremo | Pular", size=12, italic=True))
            lista_perguntas.controls.append(ft.Divider())

            global_idx = 0
            for titulo_dominio, perguntas in dominios_whosrpb:
                lista_perguntas.controls.append(
                    ft.Container(content=ft.Text(titulo_dominio, weight="bold", color="white"), bgcolor="teal",
                                 padding=5, border_radius=5))
                for q in perguntas:
                    def mudar(idx):
                        def fn(e): respostas_whosrpb[idx] = int(e.control.value)

                        return fn

                    valor_inicial = str(respostas_whosrpb[global_idx]) if respostas_whosrpb[
                                                                              global_idx] is not None else None

                    lista_perguntas.controls.append(ft.Column([
                        ft.Text(q, size=13),
                        ft.RadioGroup(
                            value=valor_inicial,
                            content=ft.Row([
                                ft.Radio(value="1", label="1"), ft.Radio(value="2", label="2"),
                                ft.Radio(value="3", label="3"), ft.Radio(value="4", label="4"),
                                ft.Radio(value="5", label="5"), ft.Radio(value="-1", label="Pular")
                                # RADIO PULAR ADICIONADO
                            ]), on_change=mudar(global_idx)
                        )
                    ]))
                    global_idx += 1
                lista_perguntas.controls.append(ft.Divider())

        def salvar_whosrpb(e):
            # A TRAVA VOLTOU
            if None in respostas_whosrpb or not campo_nome.value or not campo_inst.value or not campo_sexo.value:
                mostrar_alerta_preenchimento()
                return

            estado_memoria["lembrar_inst"] = check_inst.value;
            estado_memoria["inst"] = campo_inst.value if check_inst.value else ""
            estado_memoria["lembrar_resp"] = check_resp.value;
            estado_memoria["resp"] = campo_resp.value if check_resp.value else ""
            estado_memoria["lembrar_est"] = check_est.value;
            estado_memoria["est"] = campo_est.value if check_est.value else ""

            # Cálculo Seguro: Ignora os -1 (Pular)
            escore = sum(v for v in respostas_whosrpb if v != -1)
            pacientes_whosrpb.append({
                "nome": campo_nome.value, "sexo": campo_sexo.value, "instituicao": campo_inst.value,
                "responsavel": campo_resp.value, "estudante": campo_est.value, "escore": escore,
                "respostas": respostas_whosrpb.copy()
            })
            salvar_dados()
            ir_para_home()

        def atualizar_hist():
            view_hist.controls.clear()
            for i, p in enumerate(pacientes_whosrpb):
                classe_dinamica, cor_dinamica, conduta_dinamica = classificar_whosrpb(p['escore'])
                view_hist.controls.append(ft.Container(
                    padding=15, border=ft.border.all(1, cor_dinamica), border_radius=10,
                    margin=ft.margin.only(bottom=10),
                    content=ft.Column([
                        ft.Row([
                            ft.Text(f"Paciente: {p['nome']} ({p.get('sexo', 'N/I')})", weight="bold", size=16,
                                    expand=True),
                            ft.ElevatedButton("X", bgcolor="red", color="white",
                                              on_click=lambda _, idx=i: [pacientes_whosrpb.pop(idx), salvar_dados(),
                                                                         atualizar_hist(), page.update()])
                        ]),
                        ft.Text(f"Asilo/Inst.: {p['instituicao']}", size=14),
                        ft.Text(f"Responsável: {p['responsavel']} | Estudante: {p['estudante']}", size=12,
                                color="grey"),
                        ft.Text(f"Escore: {p['escore']} / 160 pts - {classe_dinamica}", color=cor_dinamica,
                                weight="bold", size=14),
                        ft.Text(f"Conduta: {conduta_dinamica}", size=13)
                    ], spacing=5)
                ))

        def atualizar_fichas_detalhadas():
            view_fichas.controls.clear()
            if not pacientes_whosrpb:
                view_fichas.controls.append(ft.Text("Nenhum paciente cadastrado.", color="grey"))
                return

            for p in pacientes_whosrpb:
                coluna_respostas = ft.Column(spacing=2)
                resps = p.get("respostas", [])

                if not resps:
                    coluna_respostas.controls.append(
                        ft.Text("⚠️ Respostas detalhadas não registradas nas versões anteriores.", color="red",
                                size=12))
                else:
                    global_idx = 0
                    for titulo_dominio, perguntas in dominios_whosrpb:
                        coluna_respostas.controls.append(ft.Text(titulo_dominio, weight="bold", size=13, color="teal"))
                        for q in perguntas:
                            if global_idx < len(resps):
                                val = resps[global_idx]
                                txt_val = val if val != -1 else "Não Respondeu (Pulo)"
                                coluna_respostas.controls.append(
                                    ft.Text(f"{q[:35]}... ➔ Nota: {txt_val}", size=11, color="grey800"))
                            global_idx += 1

                view_fichas.controls.append(ft.Container(
                    padding=15, border=ft.border.all(1, "grey400"), border_radius=10, margin=ft.margin.only(bottom=15),
                    bgcolor="grey50",
                    content=ft.Column([
                        ft.Text(f"📝 Ficha Detalhada: {p['nome']} ({p.get('sexo', 'N/I')})", weight="bold", size=16,
                                color="teal"),
                        ft.Text(f"Asilo: {p['instituicao']} | Escore Total: {p['escore']} pts", size=13, weight="bold"),
                        ft.Divider(),
                        coluna_respostas
                    ])
                ))

        render_perguntas()
        view_ficha = ft.Column([
            lista_perguntas,
            ft.ElevatedButton("SALVAR WHO-SRPB", bgcolor="teal", color="white", height=50, width=1000,
                              on_click=salvar_whosrpb)
        ], expand=True)

        page.add(ft.Column([
            ft.Row([ft.ElevatedButton("< MENU", on_click=ir_para_home),
                    ft.Text("WHO-SRPB", size=20, weight="bold", color="teal")]),
            ft.Row([btn_f, btn_h, btn_det], alignment="center"),
            ft.Divider(), view_ficha, view_hist, view_fichas
        ], expand=True))

    # --- TELA DE RELATÓRIOS (GRÁFICOS E TABELA) ---
    def abrir_relatorios(e):
        page.clean()
        area_relatorios = ft.Column(scroll="always", expand=True, spacing=30)

        instituicoes = set()
        for p in pacientes_gds + pacientes_facit + pacientes_whosrpb:
            instituicoes.add(p["instituicao"])

        if not instituicoes:
            area_relatorios.controls.append(ft.Text("Nenhum dado cadastrado ainda.", size=18, color="grey"))
        else:
            # 1. GERAR GRÁFICOS
            area_relatorios.controls.append(ft.Text("RESUMO DOS ASILOS", size=20, weight="bold"))
            for inst in sorted(instituicoes):
                gds_inst = [p["escore"] for p in pacientes_gds if p["instituicao"] == inst]
                facit_inst = [p["escore"] for p in pacientes_facit if p["instituicao"] == inst]
                whosrpb_inst = [p["escore"] for p in pacientes_whosrpb if p["instituicao"] == inst]

                media_gds = sum(gds_inst) / len(gds_inst) if gds_inst else 0
                media_facit = sum(facit_inst) / len(facit_inst) if facit_inst else 0
                media_whosrpb = sum(whosrpb_inst) / len(whosrpb_inst) if whosrpb_inst else 0

                altura_max = 150

                def criar_barra(media, maximo, cor):
                    altura = int((media / maximo) * altura_max) if media > 0 else 5
                    if altura < 25: altura = 25

                    return ft.Container(
                        width=60, height=altura, bgcolor=cor, border_radius=5,
                        content=ft.Row([ft.Text(f"{media:.1f}", color="white", weight="bold")], alignment="center")
                    )

                bar_gds = criar_barra(media_gds, 15, "blue")
                bar_facit = criar_barra(media_facit, 36, "purple")
                bar_whosrpb = criar_barra(media_whosrpb, 160, "teal")

                area_relatorios.controls.append(
                    ft.Container(
                        padding=15, border=ft.border.all(1, "grey300"), border_radius=10,
                        content=ft.Column([
                            ft.Text(f"📊 ASILO: {inst}", size=18, weight="bold"),
                            ft.Text("Média Geral de Pontuação", size=12, color="grey"),
                            ft.Container(height=20),
                            ft.Row([
                                ft.Column([bar_gds, ft.Text("GDS\n(Max 15)", size=10, text_align="center")],
                                          horizontal_alignment="center"),
                                ft.Column([bar_facit, ft.Text("FACIT\n(Max 36)", size=10, text_align="center")],
                                          horizontal_alignment="center"),
                                ft.Column([bar_whosrpb, ft.Text("WHO-SRPB\n(Max 160)", size=10, text_align="center")],
                                          horizontal_alignment="center"),
                            ], alignment="center", spacing=40, vertical_alignment="end", height=altura_max + 50)
                        ])
                    )
                )

            # 2. GERAR TABELA ANÔNIMA DE PACIENTES
            area_relatorios.controls.append(ft.Divider())
            area_relatorios.controls.append(ft.Text("LISTAGEM DE PACIENTES (ANÔNIMA)", size=20, weight="bold"))
            area_relatorios.controls.append(
                ft.Text("Os nomes foram ocultados. Pacientes que fizeram mais de um teste foram unificados.", size=12,
                        color="grey"))

            pacientes_unificados = {}

            def mesclar_paciente(p, teste_nome, valor):
                chave = f"{p['nome'].strip().lower()}_{p['instituicao'].strip().lower()}"
                if chave not in pacientes_unificados:
                    pacientes_unificados[chave] = {
                        "inst": p['instituicao'], "sexo": p.get('sexo', 'N/I'), "gds": "-", "facit": "-", "who": "-"
                    }
                pacientes_unificados[chave][teste_nome] = valor

            for p in pacientes_gds: mesclar_paciente(p, "gds", classificar_gds15(p["escore"])[0])
            for p in pacientes_facit: mesclar_paciente(p, "facit", classificar_facit(p["escore"]))
            for p in pacientes_whosrpb: mesclar_paciente(p, "who", classificar_whosrpb(p["escore"])[0])

            def copiar_para_excel(e):
                linhas = ["Instituição\tSexo\tGDS\tFACIT-Sp\tWHO-SRPB"]
                for info in pacientes_unificados.values():
                    linha = f"{info['inst']}\t{info['sexo']}\t{info['gds']}\t{info['facit']}\t{info['who']}"
                    linhas.append(linha)

                page.set_clipboard("\n".join(linhas))
                e.control.text = "✔️ Copiado! Pressione CTRL+V no Excel"
                e.control.bgcolor = "green"
                page.update()

            btn_copiar = ft.ElevatedButton("Copiar Tabela para Excel", bgcolor="black", color="white",
                                           on_click=copiar_para_excel)
            area_relatorios.controls.append(btn_copiar)

            tabela = ft.DataTable(
                columns=[
                    ft.DataColumn(ft.Text("Instituição", weight="bold")), ft.DataColumn(ft.Text("Sexo", weight="bold")),
                    ft.DataColumn(ft.Text("GDS", weight="bold")), ft.DataColumn(ft.Text("FACIT-Sp", weight="bold")),
                    ft.DataColumn(ft.Text("WHO-SRPB", weight="bold")),
                ],
                rows=[]
            )

            for info in pacientes_unificados.values():
                tabela.rows.append(ft.DataRow(cells=[
                    ft.DataCell(ft.Text(info["inst"])), ft.DataCell(ft.Text(info["sexo"])),
                    ft.DataCell(ft.Text(info["gds"])),
                    ft.DataCell(ft.Text(info["facit"])), ft.DataCell(ft.Text(info["who"])),
                ]))

            area_relatorios.controls.append(ft.Row([tabela], scroll="always"))

        page.add(ft.Column([
            ft.Row([ft.ElevatedButton("< MENU", on_click=ir_para_home),
                    ft.Text("Relatórios e Tabelas", size=20, weight="bold")]),
            ft.Divider(), area_relatorios
        ], expand=True))

    # --- FUNÇÃO APAGAR TUDO ---
    def confirmar_apagar(e):
        pacientes_gds.clear();
        pacientes_facit.clear();
        pacientes_whosrpb.clear()
        estado_memoria["inst"] = "";
        estado_memoria["resp"] = "";
        estado_memoria["est"] = ""
        salvar_dados()
        dialogo_apagar.open = False
        page.update();
        ir_para_home()

    def cancelar_apagar(e):
        dialogo_apagar.open = False;
        page.update()

    dialogo_apagar = ft.AlertDialog(
        title=ft.Text("Apagar banco de dados?"),
        content=ft.Text(
            "ATENÇÃO: Essa ação apagará PERMANENTEMENTE todos os pacientes cadastrados e históricos. Deseja continuar?"),
        actions=[
            ft.ElevatedButton("Cancelar", color="black", bgcolor="grey300", on_click=cancelar_apagar),
            ft.ElevatedButton("Sim, apagar tudo", color="white", bgcolor="red", on_click=confirmar_apagar),
        ], actions_alignment="end",
    )

    def abrir_dialogo_apagar(e):
        page.overlay.append(dialogo_apagar);
        dialogo_apagar.open = True;
        page.update()

    # --- HOME ---
    def renderizar_home():
        def alternar_dev(e): estado_memoria["modo_dev"] = e.control.value

        return ft.Column([
            ft.Text("GERIATRIA PRO", size=35, weight="bold", color="blue800"),
            ft.Text("Selecione o teste abaixo:", size=14, color="grey"),
            ft.Container(height=10),
            ft.ElevatedButton(
                content=ft.Container(content=ft.Column(
                    [ft.Text("GDS-15", size=20, weight="bold"), ft.Text("Depressão Geriátrica", size=11)],
                    alignment="center", horizontal_alignment="center")),
                width=350, height=70, bgcolor="blue", color="white", on_click=abrir_gds
            ),
            ft.Container(height=5),
            ft.ElevatedButton(
                content=ft.Container(content=ft.Column(
                    [ft.Text("FACIT-Sp-9", size=20, weight="bold"), ft.Text("Saúde Espiritual", size=11)],
                    alignment="center", horizontal_alignment="center")),
                width=350, height=70, bgcolor="purple", color="white", on_click=abrir_facit
            ),
            ft.Container(height=5),
            ft.ElevatedButton(
                content=ft.Container(content=ft.Column(
                    [ft.Text("WHO-SRPB", size=20, weight="bold"), ft.Text("Qualidade de Vida e Resiliência", size=11)],
                    alignment="center", horizontal_alignment="center")),
                width=350, height=70, bgcolor="teal", color="white", on_click=abrir_whosrpb
            ),
            ft.Container(height=5),
            ft.ElevatedButton(
                content=ft.Container(content=ft.Row([ft.Text("📊 VER RELATÓRIOS E TABELAS", size=14, weight="bold")],
                                                    alignment="center")),
                width=350, height=50, bgcolor="grey800", color="white", on_click=abrir_relatorios
            ),
            ft.Container(height=10),
            ft.Container(
                content=ft.Row([
                    ft.Column([ft.Text(str(len(pacientes_gds)), size=20, weight="bold"), ft.Text("GDS", size=10)],
                              horizontal_alignment="center"),
                    ft.VerticalDivider(width=20),
                    ft.Column([ft.Text(str(len(pacientes_facit)), size=20, weight="bold"), ft.Text("FACIT", size=10)],
                              horizontal_alignment="center"),
                    ft.VerticalDivider(width=20),
                    ft.Column(
                        [ft.Text(str(len(pacientes_whosrpb)), size=20, weight="bold"), ft.Text("WHO-SRPB", size=10)],
                        horizontal_alignment="center"),
                ], alignment="center"), padding=10, bgcolor="grey100", border_radius=10, width=350
            ),
            ft.Container(height=20),
            ft.Checkbox(label="Ativar Modo Desenvolvedor (Preenchimento Aleatório)", value=estado_memoria["modo_dev"],
                        on_change=alternar_dev),
            ft.Container(height=20),
            ft.ElevatedButton("Apagar Todos os Dados do App", color="white", bgcolor="red", width=350, height=50,
                              on_click=abrir_dialogo_apagar)
        ], alignment="center", horizontal_alignment="center", expand=True)

    page.add(renderizar_home())


ft.app(target=main)