import functions_framework
import firebase_admin
from firebase_admin import credentials, firestore, storage
import os
from functions.calcular_viabilidade_pastagem import calcular_viabilidade_pastagem
from functions.estimar_lotacao_suporte import estimar_lotacao_suporte

# Inicializar Firebase Admin SDK
if not firebase_admin._apps:
    cred = credentials.ApplicationDefault()
    firebase_admin.initialize_app(cred, {
        'storageBucket': os.environ.get('FIREBASE_STORAGE_BUCKET', 'regenerative-pasture.appspot.com')
    })

db = firestore.client()
storage_client = storage.bucket()

# ==================== FUNÇÃO 1: CALCULAR VIABILIDADE ====================
@functions_framework.http
def calcular_viabilidade_pastagem_http(request):
    request_json = request.get_json(silent=True)
    try:
        result = calcular_viabilidade_pastagem(request_json, db)
        return {'status': 'success', 'data': result}, 200
    except ValueError as e:
        return {'status': 'error', 'message': str(e)}, 400
    except Exception as e:
        return {'status': 'error', 'message': f'Erro interno: {str(e)}'}, 500


# ==================== FUNÇÃO 2: ESTIMAR LOTAÇÃO ====================
@functions_framework.http
def estimar_lotacao_suporte_http(request):
    request_json = request.get_json(silent=True)
    try:
        result = estimar_lotacao_suporte(request_json, db)
        return {'status': 'success', 'data': result}, 200
    except ValueError as e:
        return {'status': 'error', 'message': str(e)}, 400
    except Exception as e:
        return {'status': 'error', 'message': f'Erro interno: {str(e)}'}, 500
