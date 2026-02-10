import cv2
from ultralytics import YOLO
import sys
from datetime import datetime

# --- CONFIGURAÇÕES ---
MODEL_PATH = 'best.pt'
IMAGE_PATH = 'guidance-arch.jpg' 
CONFIDENCE = 0.01  

# --- FILTRO DE RUÍDO ---
IGNORE_CLASSES = [
    'groups', 'aws', 'aws cloud', 'availability zone', 
    'public subnet', 'private subnet', 'text', 'vpc', 'region'
]

# --- 1. O TRADUTOR ---
CATEGORY_MAPPING = {
    'database': [
        'sql', 'db', 'database', 'rds', 'dynamo', 'storage', 's3', 'bucket', 
        'blob', 'data', 'store', 'cache', 'redis', 'oracle', 'mysql', 'postgres',
        'analytics', 'athena', 'glue', 'kinesis', 'lake', 'warehouse',
        'solr', 'elasticache', 'memcached', 'volume', 'drive', 'aurora'
    ],
    'server': [
        'ec2', 'vm', 'server', 'compute', 'instance', 'lambda', 'function', 
        'app service', 'container', 'kubernetes', 'eks', 'aks', 'fargate', 'node',
        'beanstalk', 'batch', 'lightsail', 'scale set', 'virtual machine',
        'sei / sip', 'auto scaling', 'logic app'
    ],
    'gateway': [
        'gateway', 'load balancer', 'elb', 'alb', 'firewall', 'waf', 'route', 
        'cdn', 'cloudfront', 'traffic', 'hub', 'manager', 'shield', 'network',
        'v-net', 'vnet', 'front door', 'internet', 'application load balancer'
    ],
    'auth': [
        'cognito', 'active directory', 'iam', 'auth', 'key', 'secret', 'identity',
        'directory', 'sso', 'organization', 'key vault', 'tenant', 'kms'
    ]
}

# --- 2. BASE DE CONHECIMENTO STRIDE ---
STRIDE_KNOWLEDGE_BASE = {
    'database': {
        'risk': 'ALTO',
        'threats': [
            "Tampering: Modificação não autorizada de dados.",
            "Information Disclosure: Vazamento de dados sensíveis.",
            "Denial of Service: Sobrecarga de queries."
        ],
        'mitigations': [
            "✅ Criptografia em repouso (TDE) e em trânsito (TLS).",
            "✅ Backups imutáveis e segregados.",
            "✅ Princípio do menor privilégio."
        ]
    },
    'server': {
        'risk': 'MÉDIO',
        'threats': [
            "Elevation of Privilege: Exploração de bugs para root.",
            "Tampering: Injeção de malware/código.",
            "Denial of Service: Esgotamento de recursos."
        ],
        'mitigations': [
            "✅ Patch Management rigoroso.",
            "✅ EDR/HIDS para monitoramento.",
            "✅ Hardening do Sistema Operacional."
        ]
    },
    'gateway': {
        'risk': 'CRÍTICO',
        'threats': [
            "Denial of Service: Ataque volumétrico (DDoS).",
            "Man-in-the-Middle: Interceptação de tráfego."
        ],
        'mitigations': [
            "✅ WAF (Web Application Firewall).",
            "✅ Proteção Anti-DDoS (Shield/Standard).",
            "✅ HTTPS Obrigatório (TLS 1.2+)."
        ]
    },
    'auth': {
        'risk': 'ALTO',
        'threats': [
            "Spoofing: Roubo de identidade/tokens.",
            "Information Disclosure: Vazamento de credenciais."
        ],
        'mitigations': [
            "✅ MFA (Multi-Fator) Obrigatório.",
            "✅ Rotação automática de chaves/segredos.",
            "✅ Cofre de Senhas (Vault)."
        ]
    }
}

def get_category_from_label(label):
    label_lower = label.lower()
    for category, keywords in CATEGORY_MAPPING.items():
        for keyword in keywords:
            if keyword in label_lower:
                return category
    return 'outros'

def save_markdown_report(detected_labels):
    """Gera o arquivo .md com o mesmo conteúdo do terminal."""
    filename = "relatorio_visionguard.md"
    unique_labels = sorted(list(set(detected_labels)))
    analyzed_cats = set()
    
    with open(filename, "w", encoding="utf-8") as f:
        f.write("# 🛡️ VisionGuard Architect - Relatório de Segurança\n")
        f.write(f"**Data da Análise:** {datetime.now().strftime('%d/%m/%Y %H:%M')}\n\n")
        f.write("---\n\n")
        
        f.write("## 🔍 Componentes Detectados\n")
        if not unique_labels:
            f.write("Nenhum componente crítico identificado.\n")
        else:
            for label in unique_labels:
                f.write(f"- `{label}`\n")
        
        f.write("\n---\n## 📦 Análise de Vulnerabilidades (STRIDE)\n\n")
        
        for label in unique_labels:
            cat = get_category_from_label(label)
            if cat in STRIDE_KNOWLEDGE_BASE and cat not in analyzed_cats:
                analyzed_cats.add(cat)
                data = STRIDE_KNOWLEDGE_BASE[cat]
                
                emoji = "🚨" if data['risk'] in ['CRÍTICO', 'ALTO'] else "⚠️"
                f.write(f"### {emoji} Categoria: {cat.upper()} (Risco: {data['risk']})\n")
                f.write(f"*Identificado via componente: {label}*\n\n")
                
                f.write("**🔴 Ameaças Potenciais:**\n")
                for t in data['threats']:
                    f.write(f"- {t}\n")
                
                f.write("\n**🛡️ Contramedidas Recomendadas:**\n")
                for m in data['mitigations']:
                    f.write(f"- {m}\n")
                f.write("\n---\n")
                
        f.write("\n> Relatório gerado automaticamente por VisionGuard AI")
    
    print(f"📄 Relatório Markdown salvo em: {filename}")

def generate_terminal_report(detected_labels):
    """Imprime o relatório no terminal (para a demo ao vivo)."""
    print("\n" + "="*60)
    print("🛡️  RELATÓRIO DE MODELAGEM DE AMEAÇAS (STRIDE)  🛡️")
    print("="*60 + "\n")

    unique_labels = sorted(list(set(detected_labels)))
    analyzed_categories = set()

    print(f"🔎 Componentes Detectados: {', '.join(unique_labels)}\n")
    print("-" * 60)

    for label in unique_labels:
        category = get_category_from_label(label)
        if category in STRIDE_KNOWLEDGE_BASE and category not in analyzed_categories:
            analyzed_categories.add(category)
            knowledge = STRIDE_KNOWLEDGE_BASE[category]

            print(f"\n📦 ANÁLISE: {category.upper()} (Risco: {knowledge['risk']})")
            print(f"   ⚠️  AMEAÇAS:")
            for threat in knowledge['threats']: print(f"      🔴 {threat}")
            print(f"   🛡️  CONTRAMEDIDAS:")
            for mitigation in knowledge['mitigations']: print(f"      🟢 {mitigation}")
            print("-" * 30)
    print("\n✅ Fim do Relatório.")
    print("="*60)

def main():
    print("🧠 Carregando VisionGuard Architect...")
    try:
        model = YOLO(MODEL_PATH)
    except:
        print(f"❌ Erro: {MODEL_PATH} não encontrado.")
        return

    img = cv2.imread(IMAGE_PATH)
    if img is None:
        print(f"❌ Erro ao abrir {IMAGE_PATH}")
        return

    print("🔍 Analisando arquitetura...")
    results = model(img, conf=CONFIDENCE)
    
    final_labels = []
    
    annotated_frame = img.copy()

    for r in results:
        for box in r.boxes:
            cls_id = int(box.cls[0])
            label_name = model.names[cls_id]
            conf = float(box.conf[0])
            
            label_lower = label_name.lower()
            if any(ignore in label_lower for ignore in IGNORE_CLASSES):
                continue
            
            final_labels.append(label_name)
            

            x1, y1, x2, y2 = map(int, box.xyxy[0])
            
            color = (0, 255, 0) 
            cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), color, 2)
            
            text = f"{label_name} {conf:.2f}"
            cv2.putText(annotated_frame, text, (x1, y1 - 10), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

    cv2.imshow("VisionGuard - Analise", annotated_frame)
    cv2.imwrite("resultado_limpo.jpg", annotated_frame)
    print("📸 Imagem limpa salva como 'resultado_limpo.jpg'")

    generate_terminal_report(final_labels)

    save_markdown_report(final_labels)

    print("\nℹ️  Pressione qualquer tecla na imagem para encerrar...")
    cv2.waitKey(0)
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()