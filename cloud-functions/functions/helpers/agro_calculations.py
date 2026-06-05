import numpy as np

def calcular_custo_operacional(horas_trator_ha, area_ha, custo_hora_reais, custo_sementes_ha=0, custo_insumos_ha=200):
    """Calcula custo operacional total de intervenção na pastagem."""
    custo_trator = horas_trator_ha * area_ha * custo_hora_reais
    custo_sementes_total = custo_sementes_ha * area_ha
    custo_insumos_total = custo_insumos_ha * area_ha
    return custo_trator + custo_sementes_total + custo_insumos_total

def estimar_biomassa_ndvi(ndvi, kg_ms_ha_base, ndvi_otimo, fator_ndvi=1.0):
    """Estima biomassa disponível baseada em NDVI."""
    ndvi_normalizado = max(0, ndvi)
    biomassa_estimada = kg_ms_ha_base * (ndvi_normalizado / ndvi_otimo) * fator_ndvi
    biomassa_minima = kg_ms_ha_base * 0.15
    biomassa_maxima = kg_ms_ha_base * 1.15
    return float(np.clip(biomassa_estimada, biomassa_minima, biomassa_maxima))

def calcular_capacidade_suporte(biomassa_disponivel_kg_ms_ha, consumo_diario_ua_kg_ms=11.25, dias_ciclo=30, fator_seguranca=1.0):
    """Calcula UA/ha baseado em biomassa e consumo animal."""
    ua_ha = (biomassa_disponivel_kg_ms_ha / (consumo_diario_ua_kg_ms * dias_ciclo)) * fator_seguranca
    return float(max(0, ua_ha))

def calcular_roi_anual(receita_ha_reais, custo_ha_reais, anos=1):
    """Calcula retorno sobre investimento (ROI) em porcentagem."""
    if custo_ha_reais <= 0:
        return 0.0
    roi = ((receita_ha_reais - custo_ha_reais) / custo_ha_reais) * 100 / anos
    return float(roi)
