"""
Facebook Graph API Connector
Conecta ao Facebook e puxa posts, comentários, reações e insights
"""

import requests
import os
from datetime import datetime
from dotenv import load_dotenv
import json
from typing import Dict, List, Optional

load_dotenv()

class FacebookConnector:
    """Conecta à Graph API do Facebook"""
    
    def __init__(self):
        """Inicializa o conector com credenciais"""
        self.page_id = os.getenv('FACEBOOK_PAGE_ID')
        self.access_token = os.getenv('FACEBOOK_ACCESS_TOKEN')
        self.api_version = os.getenv('FACEBOOK_API_VERSION', 'v25.0')
        self.debug_mode = os.getenv('DEBUG_MODE', 'False').lower() == 'true'
        
        self.base_url = f"https://graph.facebook.com/{self.api_version}"
        
        if not self.page_id or not self.access_token:
            raise ValueError("❌ Credenciais do Facebook não configuradas no .env!")
        
        print("✅ Facebook Connector inicializado com sucesso!")
    
    def _fazer_requisicao(self, endpoint: str, metodo: str = 'GET', 
                         parametros: Dict = None) -> Optional[Dict]:
        """Faz requisição à Graph API"""
        try:
            url = f"{self.base_url}{endpoint}"
            
            if parametros is None:
                parametros = {}
            parametros['access_token'] = self.access_token
            
            if metodo == 'GET':
                resposta = requests.get(url, params=parametros, timeout=10)
            else:
                resposta = requests.post(url, json=parametros, timeout=10)
            
            if resposta.status_code != 200:
                print(f"⚠️ Erro na requisição: {resposta.status_code}")
                return None
            
            return resposta.json()
            
        except Exception as e:
            print(f"❌ Erro: {e}")
            return None
    
    def obter_posts(self, limite: int = 10) -> List[Dict]:
        """Obtém posts recentes da página"""
        print(f"\n📱 Buscando {limite} posts recentes...")
        
        endpoint = f"/{self.page_id}/posts"
        parametros = {
            'fields': 'id,message,created_time,type,story,permalink_url',
            'limit': limite,
            'access_token': self.access_token
        }
        
        resposta = self._fazer_requisicao(endpoint, parametros=parametros)
        
        if not resposta or 'data' not in resposta:
            print("❌ Nenhum post encontrado!")
            return []
        
        posts = []
        for post in resposta['data']:
            posts.append({
                'id': post.get('id'),
                'mensagem': post.get('message', post.get('story', 'Sem texto')),
                'data': post.get('created_time'),
                'tipo': post.get('type'),
                'link': post.get('permalink_url')
            })
        
        print(f"✅ {len(posts)} posts encontrados!")
        return posts
    
    def obter_dados_completos(self, num_posts: int = 5) -> Dict:
        """Obtém dados completos"""
        print("\n" + "="*60)
        print("🚀 INICIANDO EXTRAÇÃO COMPLETA DE DADOS")
        print("="*60)
        
        dados = {
            'data_extracao': datetime.now().isoformat(),
            'page_id': self.page_id,
            'posts': [],
            'insights': {}
        }
        
        posts = self.obter_posts(limite=num_posts)
        dados['posts'] = posts
        
        print("\n" + "="*60)
        print("✅ EXTRAÇÃO COMPLETA FINALIZADA!")
        print("="*60 + "\n")
        
        return dados
    
    def exibir_resumo(self, dados: Dict):
        """Exibe um resumo dos dados coletados"""
        print("\n" + "="*60)
        print("📈 RESUMO DOS DADOS COLETADOS")
        print("="*60)
        
        print(f"\n📅 Data: {dados['data_extracao']}")
        print(f"📄 Total de posts: {len(dados['posts'])}")
        
        print("\n" + "="*60 + "\n")


if __name__ == "__main__":
    try:
        fb = FacebookConnector()
        dados = fb.obter_dados_completos(num_posts=5)
        fb.exibir_resumo(dados)
        
    except Exception as e:
        print(f"❌ Erro fatal: {e}")
