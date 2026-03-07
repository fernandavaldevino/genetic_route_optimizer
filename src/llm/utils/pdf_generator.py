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
