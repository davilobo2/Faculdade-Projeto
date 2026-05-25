import flet as ft

# --- TEXTOS CLÍNICOS E REGRAS ---
TEXTOS_CLINICOS = {
    "Leve": """Sintomas Comuns: Desânimo leve, perda de interesse em algumas atividades (anedonia), sensação de fadiga, pessimismo e alterações sutis no sono ou apetite. O idoso ainda mantém a maior parte da funcionalidade.

Tratamento Sugerido:
• Não Farmacológico (Primeira Linha): Psicoterapia (TCC é muito eficaz), aumento da socialização, exercícios físicos supervisionados e higiene do sono.
• Monitoramento: "Espera vigilante" com reavaliação em 2 a 4 semanas. Se não houver melhora, considera-se medicação.""",

    "Moderada": """Sintomas Comuns: Sentimento de inutilidade, choro frequente, irritabilidade, dificuldade de concentração, isolamento social voluntário e redução clara no autocuidado (higiene, medicação de outras doenças).

Tratamento Sugerido:
• Combinado: Psicoterapia associada a antidepressivos (geralmente Inibidores Seletivos de Recaptação de Serotonina - ISRS, como Sertralina ou Escitalopram, devido ao perfil de segurança no idoso).
• Suporte: Avaliação de rede de apoio familiar para garantir a adesão ao tratamento.""",

    "Grave": """Sintomas Comuns: Desesperança profunda, ideação suicida (direta ou passiva, como parar de comer/beber), delírios ou alucinações (raro, mas possível), retardo psicomotor severo ou agitação intensa. Risco alto de negligência total.

Tratamento Sugerido:
• Farmacológico Intensivo: Antidepressivos em doses otimizadas, às vezes com potencializadores (antipsicóticos em doses baixas se houver sintomas psicóticos ou agitação).
• Intervenção Imediata: Avaliação psiquiátrica urgente. Em casos de risco de vida ou resistência a medicamentos, a Eletroconvulsoterapia (ECT) é considerada segura e altamente eficaz para idosos.
• Hospitalização: Considerar se houver risco de autoextermínio ou desnutrição grave."""
}

OBSERVACOES_CRUCIAIS = """Observações Cruciais para o Médico:
• Polifarmácia: Antes de prescrever, verifique se medicamentos em uso (ex: corticoides, betabloqueadores) estão causando sintomas depressivos.
• Pseudodemência: Sintomas de depressão no idoso podem mimetizar demência (perda de memória). No tratamento da depressão, a memória costuma melhorar.
• Luto vs. Depressão: Diferencie se os sintomas estão ligados a uma perda recente, embora o luto prolongado também possa exigir intervenção."""

# Lista de perguntas (Adicione as 30 perguntas da GDS aqui)
PERGUNTAS = [
    "1. Você sente que sua vida está vazia?",
    "2. Você acha que é maravilhoso estar vivo agora?",
    "3. Você prefere ficar em casa do que sair e fazer coisas novas?",
    "4. Você se sente cheio de energia?",
    "5. Você acha que a sua situação é sem esperança?"
]
# Preenchendo até 30 para o protótipo funcionar corretamente
while len(PERGUNTAS) < 30:
    PERGUNTAS.append(f"{len(PERGUNTAS) + 1}. [Insira a pergunta da GDS aqui]")

# Banco de dados temporário
pacientes = []


def classificar_gds(escore):
    if escore <= 10:
        return "Sem depressão", ft.colors.GREEN_500, "Paciente dentro da normalidade."
    elif 11 <= escore <= 20:
        return "Depressão Leve", ft.colors.YELLOW_800, TEXTOS_CLINICOS["Leve"]
    elif 21 <= escore <= 25:
        return "Depressão Moderada", ft.colors.ORANGE_500, TEXTOS_CLINICOS["Moderada"]
    else:
        return "Depressão Grave", ft.colors.RED_500, TEXTOS_CLINICOS["Grave"]


def main(page: ft.Page):
    page.title = "GDS Explorer"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.window_width = 450
    page.window_height = 800
    page.padding = 20
    page.scroll = ft.ScrollMode.AUTO

    # --- Variáveis de Estado do Passo 1 ---
    respostas_atuais = [None] * len(PERGUNTAS)  # Guarda 1 (Sim) ou 0 (Não)
    input_estudante = ft.TextField(label="Nome do Avaliador (Estudante)", width=380)
    input_paciente = ft.TextField(label="Nome do Paciente", width=380)

    # --- Elementos do Passo 2 ---
    estatisticas_text = ft.Text(size=16, weight=ft.FontWeight.BOLD)
    lista_pacientes_ui = ft.Column(scroll=ft.ScrollMode.AUTO, expand=True)

    # --- Atualização Visual das Perguntas ---
    def criar_lista_perguntas():
        coluna_perguntas = ft.Column(spacing=20)

        for i, pergunta in enumerate(PERGUNTAS):
            # Lógica para mudar a cor se estiver selecionado
            cor_sim = ft.colors.GREEN if respostas_atuais[i] == 1 else ft.colors.GREEN_100
            cor_nao = ft.colors.PURPLE if respostas_atuais[i] == 0 else ft.colors.PURPLE_100

            btn_sim = ft.Container(
                content=ft.Text("Sim", color=ft.colors.WHITE if respostas_atuais[i] == 1 else ft.colors.BLACK,
                                weight=ft.FontWeight.BOLD),
                width=60, height=60, border_radius=30, bgcolor=cor_sim,
                alignment=ft.alignment.center,
                on_click=lambda e, idx=i: selecionar_resposta(idx, 1)
            )

            btn_nao = ft.Container(
                content=ft.Text("Não", color=ft.colors.WHITE if respostas_atuais[i] == 0 else ft.colors.BLACK,
                                weight=ft.FontWeight.BOLD),
                width=60, height=60, border_radius=30, bgcolor=cor_nao,
                alignment=ft.alignment.center,
                on_click=lambda e, idx=i: selecionar_resposta(idx, 0)
            )

            linha_pergunta = ft.Column([
                ft.Text(pergunta, weight=ft.FontWeight.W_500, size=16),
                ft.Row([btn_sim, btn_nao], alignment=ft.MainAxisAlignment.CENTER, spacing=30),
                ft.Divider()
            ])
            coluna_perguntas.controls.append(linha_pergunta)

        return coluna_perguntas

    container_perguntas = ft.Container(content=criar_lista_perguntas())

    def selecionar_resposta(index, valor):
        respostas_atuais[index] = valor
        container_perguntas.content = criar_lista_perguntas()
        page.update()

    def limpar_form():
        input_estudante.value = ""
        input_paciente.value = ""
        for i in range(len(respostas_atuais)):
            respostas_atuais[i] = None
        container_perguntas.content = criar_lista_perguntas()
        page.update()

    def salvar_teste(e):
        if None in respostas_atuais:
            page.snack_bar = ft.SnackBar(ft.Text("Por favor, responda todas as perguntas antes de salvar."))
            page.snack_bar.open = True
            page.update()
            return

        if not input_estudante.value or not input_paciente.value:
            page.snack_bar = ft.SnackBar(ft.Text("Preencha o nome do paciente e do estudante."))
            page.snack_bar.open = True
            page.update()
            return

        escore = sum(respostas_atuais)  # Soma todos os 1s
        classificacao, cor, texto_tratamento = classificar_gds(escore)

        dados = {
            "estudante": input_estudante.value,
            "paciente": input_paciente.value,
            "escore": escore,
            "classificacao": classificacao,
            "cor": cor,
            "detalhes": texto_tratamento
        }

        pacientes.append(dados)
        page.snack_bar = ft.SnackBar(ft.Text("Teste salvo com sucesso!"))
        page.snack_bar.open = True

        limpar_form()
        atualizar_passo2()
        mostrar_dialogo_resultado(dados)

    btn_salvar = ft.ElevatedButton(
        "Salvar Respostas e Gerar Relatório",
        on_click=salvar_teste,
        width=380,
        bgcolor=ft.colors.BLUE_GREY_700,
        color=ft.colors.WHITE,
        height=50
    )

    passo1_view = ft.Column([
        ft.Text("Avaliação GDS - Depressão Geriátrica", size=22, weight=ft.FontWeight.BOLD,
                text_align=ft.TextAlign.CENTER),
        ft.Container(height=10),
        input_paciente,
        input_estudante,
        ft.Divider(),
        container_perguntas,
        btn_salvar
    ], alignment=ft.MainAxisAlignment.START, horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        scroll=ft.ScrollMode.AUTO)

    # --- Funções do Passo 2 ---
    def excluir_paciente(index):
        pacientes.pop(index)
        atualizar_passo2()

    def atualizar_passo2():
        normais = sum(1 for p in pacientes if p["escore"] <= 10)
        leves = sum(1 for p in pacientes if 11 <= p["escore"] <= 20)
        moderados = sum(1 for p in pacientes if 21 <= p["escore"] <= 25)
        graves = sum(1 for p in pacientes if p["escore"] >= 26)

        estatisticas_text.value = f"Total de Avaliações: {len(pacientes)}\nNormais: {normais} | Leves: {leves} | Mod.: {moderados} | Graves: {graves}"

        lista_pacientes_ui.controls.clear()
        for i, p in enumerate(pacientes):
            card = ft.Container(
                bgcolor=ft.colors.WHITE,
                border=ft.border.all(2, p["cor"]),
                border_radius=10,
                padding=15,
                margin=ft.margin.only(bottom=10),
                content=ft.Column([
                    ft.Text(f"Paciente: {p['paciente']}", weight=ft.FontWeight.BOLD, size=16),
                    ft.Text(f"Avaliador: {p['estudante']} | Escore: {p['escore']}", size=14, color=ft.colors.GREY_700),
                    ft.Text(f"Classificação: {p['classificacao']}", color=p["cor"], weight=ft.FontWeight.BOLD),
                    ft.Row([
                        ft.IconButton(ft.icons.DELETE_OUTLINE, icon_color=ft.colors.RED,
                                      on_click=lambda e, idx=i: excluir_paciente(idx), tooltip="Excluir"),
                        ft.IconButton(ft.icons.INFO_OUTLINE, icon_color=ft.colors.BLUE,
                                      on_click=lambda e, p_data=p: mostrar_dialogo_resultado(p_data),
                                      tooltip="Ver Detalhes Clínicos")
                    ], alignment=ft.MainAxisAlignment.END)
                ])
            )
            lista_pacientes_ui.controls.append(card)
        page.update()

    passo2_view = ft.Column([
        ft.Text("Visão Geral das Estatísticas", size=22, weight=ft.FontWeight.BOLD),
        estatisticas_text,
        ft.Divider(),
        ft.Text("Lista de Pacientes", size=18, weight=ft.FontWeight.BOLD),
        lista_pacientes_ui
    ], expand=True)

    # --- Diálogo de Detalhes ---
    def mostrar_dialogo_resultado(dados):
        dlg = ft.AlertDialog(
            title=ft.Text(f"Resultado: {dados['classificacao']}", color=dados["cor"]),
            content=ft.Column([
                ft.Text(f"Paciente: {dados['paciente']} | Escore: {dados['escore']}", weight=ft.FontWeight.BOLD),
                ft.Divider(),
                ft.Text(dados['detalhes'], size=14),
                ft.Divider(),
                ft.Text(OBSERVACOES_CRUCIAIS, weight=ft.FontWeight.BOLD, color=ft.colors.RED_900, size=13)
            ], scroll=ft.ScrollMode.AUTO, height=450),
            actions=[ft.TextButton("Fechar", on_click=lambda e: fechar_dialogo(dlg))],
        )
        page.dialog = dlg
        dlg.open = True
        page.update()

    def fechar_dialogo(dlg):
        dlg.open = False
        page.update()

    # --- Estrutura de Abas ---
    tabs = ft.Tabs(
        selected_index=0,
        animation_duration=300,
        tabs=[
            ft.Tab(text="Passo 1: Fazer Teste", content=ft.Container(content=passo1_view, padding=10)),
            ft.Tab(text="Passo 2: Ver Resultados", content=ft.Container(content=passo2_view, padding=10)),
        ],
        expand=True,
    )

    page.add(tabs)
    atualizar_passo2()


ft.app(target=main)