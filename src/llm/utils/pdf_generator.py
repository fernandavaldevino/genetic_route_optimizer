"""
Gerador de PDF para documentos LLM
Utiliza FPDF2 para criar PDFs formatados a partir de texto markdown
"""

from fpdf import FPDF
import re
from datetime import datetime


class PDFGenerator(FPDF):
    """ Classe personalizada para geração de PDF """
    
    def __init__(self, title="Documento"):
        super().__init__(orientation='P', unit='mm', format='A4')
        self.document_title = title
        self.set_margins(left=20, top=25, right=20)
        self.set_auto_page_break(auto=True, margin=25)
        
    def header(self):
        """ Cabeçalho """
        self.set_font('Arial', 'B', 16)
        self.cell(0, 12, self.document_title, 0, 1, 'C')
        self.ln(8)
        
    def footer(self):
        """ Rodapé """
        self.set_y(-15)
        self.set_font('Arial', 'I', 9)
        date_str = datetime.now().strftime('%d/%m/%Y %H:%M')
        self.cell(0, 10, f'Gerado em: {date_str} - Pagina {self.page_no()}', 0, 0, 'C')


def markdown_to_pdf(text: str, filename: str, title: str = "Documento", render_checkboxes: bool = False) -> bytes:
    """ Converte texto markdown para PDF com formatação melhorada """
    pdf = PDFGenerator(title=title)
    pdf.add_page()
    
    # Largura efetiva (A4 = 210mm, margens 20mm cada lado = 170mm)
    effective_width = 170
    
    # Processar o texto linha por linha
    lines = text.split('\n')
    
    i = 0
    while i < len(lines):
        line = lines[i].rstrip()
        
        # Linha vazia
        if not line.strip():
            pdf.ln(4)
            i += 1
            continue
        
        # Títulos (# ## ###)
        if line.startswith('###'):
            pdf.set_font('Arial', 'B', 11)
            clean_text = line.replace('###', '').strip()
            pdf.multi_cell(effective_width, 6, clean_text, align='L')
            pdf.ln(3)
            i += 1
        elif line.startswith('##'):
            pdf.set_font('Arial', 'B', 12)
            clean_text = line.replace('##', '').strip()
            pdf.multi_cell(effective_width, 7, clean_text, align='L')
            pdf.ln(4)
            i += 1
        elif line.startswith('#'):
            pdf.set_font('Arial', 'B', 14)
            clean_text = line.replace('#', '').strip()
            pdf.multi_cell(effective_width, 8, clean_text, align='C')
            pdf.ln(5)
            i += 1
        
        # Listas numeradas com negrito (ex: "1. **Ponto 1 - Emergência Obstétrica**" ou "**Ponto 1:**")
        elif re.match(r'^\d+\.\s+\*\*.*\*\*', line) or re.match(r'^\*\*Ponto\s+\d+', line):
            # Extrair número e texto
            if line.startswith('**'):
                # Formato: **Ponto 7:**
                match = re.match(r'^\*\*(.*?)\*\*(.*)$', line)
                if match:
                    bold_text = match.group(1)
                    rest = match.group(2)
                    
                    # Escrever texto em negrito
                    pdf.set_font('Arial', 'B', 12)
                    pdf.multi_cell(effective_width, 7, f'{bold_text}{rest}', align='L')
                    pdf.ln(2)
            else:
                # Formato: 1. **Ponto 1 - Emergência Obstétrica**
                match = re.match(r'^(\d+\.)\s+\*\*(.*?)\*\*(.*)$', line)
                if match:
                    number = match.group(1)
                    bold_text = match.group(2)
                    rest = match.group(3)
                    
                    # Escrever número e texto em negrito
                    pdf.set_font('Arial', 'B', 12)
                    pdf.multi_cell(effective_width, 7, f'{number} {bold_text}{rest}', align='L')
                    pdf.ln(2)
            i += 1
        
        # Sub-itens com indentação
        elif re.match(r'^\s{2,}[-*]\s+', line):
            # Contar espaços de indentação (mínimo 2 espaços = sub-item)
            indent_match = re.match(r'^(\s+)[-*]\s+(.*)$', line)
            if indent_match:
                indent_spaces = len(indent_match.group(1))
                bullet_text = indent_match.group(2)
                
                # Remover markdown bold (**texto**)
                has_bold = '**' in bullet_text
                clean_text = re.sub(r'\*\*(.*?)\*\*', r'\1', bullet_text)
                
                # Definir fonte (negrito se tinha **)
                if has_bold:
                    pdf.set_font('Arial', 'B', 11)
                else:
                    pdf.set_font('Arial', '', 11)
                
                # Calcular indentação (4 espaços = 10mm)
                indent_mm = (indent_spaces / 4) * 10
                
                if render_checkboxes:
                    # Verificar se há espaço suficiente na página (mínimo 10mm)
                    if pdf.get_y() > (pdf.h - pdf.b_margin - 10):
                        pdf.add_page()
                    
                    # Desenhar checkbox (quadrado vazio)
                    pdf.set_x(20 + indent_mm)
                    x_pos = pdf.get_x()
                    y_pos = pdf.get_y()
                    
                    # Desenhar quadrado do checkbox (4x4mm)
                    pdf.rect(x_pos, y_pos + 1, 4, 4)
                    
                    # Escrever texto ao lado do checkbox
                    pdf.set_x(x_pos + 6)
                    pdf.multi_cell(effective_width - indent_mm - 6, 6, clean_text, align='L')
                else:
                    # Sem checkbox, apenas hífen normal
                    pdf.set_x(20 + indent_mm)
                    pdf.multi_cell(effective_width - indent_mm, 6, f'- {clean_text}', align='L')
                
                pdf.ln(1)
            i += 1
        
        # Listas com marcadores sem indentação (itens principais - sem checkbox)
        elif re.match(r'^[-*]\s+', line):
            # Contar espaços de indentação
            indent_match = re.match(r'^(\s*)[-*]\s+(.*)$', line)
            if indent_match:
                indent_spaces = len(indent_match.group(1))
                bullet_text = indent_match.group(2)
                
                # Remover markdown bold (**texto**)
                has_bold = '**' in bullet_text
                clean_text = re.sub(r'\*\*(.*?)\*\*', r'\1', bullet_text)
                
                # Definir fonte (negrito se tinha **)
                if has_bold:
                    pdf.set_font('Arial', 'B', 11)
                else:
                    pdf.set_font('Arial', '', 11)
                
                # Calcular indentação (4 espaços = 10mm)
                indent_mm = (indent_spaces / 4) * 10
                
                # Escrever com indentação
                pdf.set_x(20 + indent_mm)
                pdf.multi_cell(effective_width - indent_mm, 6, f'- {clean_text}', align='L')
                pdf.ln(1)
            i += 1
        
        # Listas numeradas simples
        elif re.match(r'^\d+\.', line):
            pdf.set_font('Arial', 'B', 13)
            pdf.multi_cell(effective_width, 6, line, align='L')
            pdf.ln(1)
            i += 1
        
        # Texto em negrito (**texto**)
        elif '**' in line:
            pdf.set_font('Arial', 'B', 12)
            clean_line = re.sub(r'\*\*(.*?)\*\*', r'\1', line)
            pdf.multi_cell(effective_width, 6, clean_line, align='L')
            pdf.ln(2)
            i += 1
        
        # Texto normal
        else:
            pdf.set_font('Arial', '', 11)
            pdf.multi_cell(effective_width, 6, line, align='J')  # J = Justificado
            pdf.ln(2)
            i += 1
    
    # Retornar PDF como bytes
    return bytes(pdf.output(dest='S'))


def generate_manual_pdf(manual_text: str, title: str = "Manual de Instruções") -> bytes:
    """Gera PDF do manual (sem checkboxes)"""
    return markdown_to_pdf(manual_text, "manual.pdf", title, render_checkboxes=False)


def generate_itinerary_pdf(itinerary_text: str, title: str = "Roteiro Detalhado") -> bytes:
    """Gera PDF do roteiro (sem checkboxes)"""
    return markdown_to_pdf(itinerary_text, "roteiro.pdf", title, render_checkboxes=False)


def generate_checklist_pdf(checklist_text: str, title: str = "Checklist Pré-Itinerário") -> bytes:
    """Gera PDF do checklist (COM checkboxes)"""
    return markdown_to_pdf(checklist_text, "checklist.pdf", title, render_checkboxes=True)


def generate_multi_vehicle_manuals_zip(vehicles_data: list, llm_integration) -> bytes:
    """ Gera múltiplos PDFs de manuais (um por veículo) e retorna como arquivo ZIP """
    import io
    import zipfile
    from src.llm.utils.formatters import route_to_dict, format_service_priority
    from src.llm.prompts.manual_templates import format_route_for_manual, MANUAL_GENERATION_TEMPLATE, MANUAL_SYSTEM_MESSAGE
    
    # Criar buffer para o ZIP
    zip_buffer = io.BytesIO()
    
    # Gerar manual base UMA ÚNICA VEZ (conteúdo genérico que serve para todos)
    # Usar dados do primeiro veículo apenas como referência para gerar o conteúdo base
    first_vehicle = vehicles_data[0]
    route_dict = route_to_dict(first_vehicle.get('route', []), 480.0, 60.0)
    route_dict['total_distance'] = route_dict['total_distance'] * 0.1
    
    route_info, service_types = format_route_for_manual(route_dict)
    
    # Gerar manual base usando LLM (conteúdo genérico)
    prompt = MANUAL_GENERATION_TEMPLATE.format(
        route_info=route_info,
        service_types=service_types
    )
    
    base_manual = llm_integration.provider.generate_text(
        prompt=prompt,
        system_message=MANUAL_SYSTEM_MESSAGE,
        max_tokens=2000
    )
    
    # Remover cabeçalho gerado pelo LLM se existir
    if base_manual.startswith('#'):
        lines = base_manual.split('\n')
        base_manual = '\n'.join(lines[1:]).strip()
    
    # Remover seção "Missão do Dia:" gerada pela LLM (já temos no cabeçalho)
    import re
    # Remover desde "Missão do Dia:" até a próxima seção (que começa com ## ou título em negrito)
    base_manual = re.sub(
        r'Missão do Dia:.*?(?=\n\n[#*]|\n\n[A-Z][a-zç]+\s+[A-Z]|\Z)',
        '',
        base_manual,
        flags=re.DOTALL | re.IGNORECASE
    )
    base_manual = base_manual.strip()
    
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for i, vehicle_data in enumerate(vehicles_data, 1):
            # Dados específicos deste veículo
            route = vehicle_data.get('route', [])
            total_distance = vehicle_data.get('total_distance', 0)
            total_time = vehicle_data.get('total_time', 0)
            
            # Calcular informações específicas da rota DESTE veículo
            num_stops = len([p for p in route if p.id != 0])
            
            # Formatar tempo estimado em horas e minutos
            time_hours = int(total_time // 60)
            time_minutes = int(total_time % 60)
            time_formatted = f"{time_hours}h{time_minutes:02d}min"
            
            # Calcular horário de término (início 08:00 = 480 minutos)
            start_time_minutes = 480  # 08:00
            end_time_minutes = start_time_minutes + total_time
            end_hours = int(end_time_minutes // 60) % 24
            end_minutes = int(end_time_minutes % 60)
            end_time_formatted = f"{end_hours:02d}:{end_minutes:02d}"
            
            # Contar tipos de atendimento DESTE veículo
            from collections import Counter
            service_counts = Counter()
            for point in route:
                if point.id != 0:
                    priority_name = format_service_priority(point.priority)
                    service_counts[priority_name] += 1
            
            # Montar cabeçalho personalizado para este veículo com SEUS dados específicos
            header = f"""# MANUAL DE INSTRUÇÕES - VEÍCULO {i}

# MANUAL DE INSTRUÇÕES PARA EQUIPE DE TRANSPORTE - SAÚDE DA MULHER

Missão do Dia: Garantir atendimentos de qualidade e sensíveis às necessidades das pacientes ao longo da rota programada.

Informações da Rota:

- Total de Paradas: {num_stops}
- Distância Total: {total_distance:.2f} km
- Tempo Estimado: {time_formatted}
- Horário de Início: 08:00
- Horário Previsto de Término: {end_time_formatted}

Tipos de Atendimento na Rota:
"""
            
            # Adicionar tipos de atendimento DESTE veículo
            for service_type, count in sorted(service_counts.items()):
                header += f"- {service_type}: {count} parada(s)\n"
            
            header += "\n---\n\n"
            
            # Combinar cabeçalho personalizado (dados específicos) com manual base (conteúdo genérico)
            manual_with_header = header + base_manual
            
            # Gerar PDF
            pdf_bytes = generate_manual_pdf(manual_with_header, title=f"Manual Veículo {i}")
            
            # Adicionar ao ZIP
            zip_file.writestr(f"manual_veiculo_{i}.pdf", pdf_bytes)
    
    zip_buffer.seek(0)
    return zip_buffer.getvalue()


def generate_multi_vehicle_itineraries_zip(vehicles_data: list, llm_integration) -> bytes:
    """ Gera múltiplos PDFs de roteiros (um por veículo) e retorna como arquivo ZIP """
    import io
    import zipfile
    from src.core.service_points import create_service_point
    
    # Criar buffer para o ZIP
    zip_buffer = io.BytesIO()
    
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for i, vehicle_data in enumerate(vehicles_data, 1):
            # Dados específicos deste veículo
            route = vehicle_data.get('route', [])
            arrival_times = vehicle_data.get('arrival_times', [])
            total_distance = vehicle_data.get('total_distance', 0)
            total_time = vehicle_data.get('total_time', 0)
            
            # IMPORTANTE: A rota não inclui o depósito, mas o prompt espera que o depósito esteja no índice 0
            # Criar depósito fictício e adicionar no início da rota
            depot = create_service_point(0, (0, 0), 'regular', None)
            depot.service_duration = 0.0
            route_with_depot = [depot] + route
            
            # Adicionar tempo 0 para o depósito no início dos arrival_times
            arrival_times_with_depot = [0.0] + arrival_times
            
            # Gerar roteiro usando LLM
            itinerary_text = llm_integration.itinerary_generator.generate_detailed_itinerary(
                route=route_with_depot,
                arrival_times=arrival_times_with_depot,
                total_distance=total_distance,
                total_time=total_time
            )
            
            # Adicionar cabeçalho do veículo
            itinerary_with_header = f"# ROTEIRO DETALHADO - VEÍCULO {i}\n\n{itinerary_text}"
            
            # Gerar PDF
            pdf_bytes = generate_itinerary_pdf(itinerary_with_header, title=f"Roteiro Veículo {i}")
            
            # Adicionar ao ZIP
            zip_file.writestr(f"roteiro_veiculo_{i}.pdf", pdf_bytes)
    
    zip_buffer.seek(0)
    return zip_buffer.getvalue()


def generate_multi_vehicle_priorities_zip(vehicles_data: list, llm_integration) -> bytes:
    """ Gera múltiplos PDFs de resumo de prioridades (um por veículo) e retorna como arquivo ZIP """
    import io
    import zipfile
    
    # Criar buffer para o ZIP
    zip_buffer = io.BytesIO()
    
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for i, vehicle_data in enumerate(vehicles_data, 1):
            # Dados específicos deste veículo
            route = vehicle_data.get('route', [])
            
            # Gerar resumo de prioridades usando LLM (sem emojis para PDF)
            priorities_text = llm_integration.manual_generator.generate_priority_summary(
                route=route,
                include_emojis=False
            )
            
            # Adicionar cabeçalho do veículo
            priorities_with_header = f"# RESUMO DE PRIORIDADES - VEÍCULO {i}\n\n{priorities_text}"
            
            # Gerar PDF
            pdf_bytes = generate_itinerary_pdf(priorities_with_header, title=f"Prioridades Veículo {i}")
            
            # Adicionar ao ZIP
            zip_file.writestr(f"prioridades_veiculo_{i}.pdf", pdf_bytes)
    
    zip_buffer.seek(0)
    return zip_buffer.getvalue()
