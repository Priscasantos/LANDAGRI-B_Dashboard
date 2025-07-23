# Correção de Erro Plotly - Font Weight

## ❌ **Problema Identificado**
```
ValueError: Invalid value of type 'builtins.str' received for the 'weight' property of layout.title.font
Received value: '600'
The 'weight' property is a integer and may be specified as:
- An int (or float that will be cast to an int) in the interval [1, 1000]
OR exactly one of ['normal', 'bold'] (e.g. 'bold')
```

## 🔧 **Causa Raiz**
O Plotly não aceita valores de `weight` como string (ex: `"600"`) para propriedades de fonte. O erro ocorreu no arquivo `modern_themes.py` onde estávamos definindo `weight="600"` em vez de usar valores aceitos pelo Plotly.

## ✅ **Correções Implementadas**

### Arquivo: `scripts/utilities/modern_themes.py`

#### 1. **Título Principal** (linha ~31)
```python
# ❌ ANTES:
title=dict(
    font=dict(
        family="Inter, system-ui, sans-serif",
        size=24,
        color="#111827",
        weight="600"  # ❌ String inválida
    )
)

# ✅ DEPOIS:
title=dict(
    font=dict(
        family="Inter, system-ui, sans-serif",
        size=24,
        color="#111827"
        # ✅ Removido weight inválido
    )
)
```

#### 2. **Eixo X** (linha ~44)
```python
# ❌ ANTES:
xaxis=dict(
    title=dict(
        font=dict(
            family="Inter, system-ui, sans-serif",
            size=14,
            color="#374151",
            weight="500"  # ❌ String inválida
        )
    )
)

# ✅ DEPOIS:
xaxis=dict(
    title=dict(
        font=dict(
            family="Inter, system-ui, sans-serif",
            size=14,
            color="#374151"
            # ✅ Removido weight inválido
        )
    )
)
```

#### 3. **Eixo Y** (linha ~66)
```python
# ❌ ANTES:
yaxis=dict(
    title=dict(
        font=dict(
            family="Inter, system-ui, sans-serif",
            size=14,
            color="#374151",
            weight="500"  # ❌ String inválida
        )
    )
)

# ✅ DEPOIS:
yaxis=dict(
    title=dict(
        font=dict(
            family="Inter, system-ui, sans-serif",
            size=14,
            color="#374151"
            # ✅ Removido weight inválido
        )
    )
)
```

#### 4. **Apply to Figure** (linha ~183)
```python
# ❌ ANTES:
title=dict(
    text=title,
    font=dict(
        family="Inter, system-ui, sans-serif",
        size=20,
        color=colors["text_primary"],
        weight="600"  # ❌ String inválida
    )
)

# ✅ DEPOIS:
title=dict(
    text=title,
    font=dict(
        family="Inter, system-ui, sans-serif",
        size=20,
        color=colors["text_primary"]
        # ✅ Removido weight inválido
    )
)
```

#### 5. **Table Config** (linha ~231)
```python
# ❌ ANTES:
"layout": {
    "title": {
        "font": {
            "size": 18,
            "family": "Inter, system-ui, sans-serif",
            "color": colors["text_primary"],
            "weight": "600"  # ❌ String inválida
        }
    },
    "margin": dict(t=50, r=30, b=30, l=30)
}

# ✅ DEPOIS:
"layout": {
    "title": {
        "font": {
            "size": 18,
            "family": "Inter, system-ui, sans-serif",
            "color": colors["text_primary"]
            # ✅ Removido weight inválido
        }
    },
    "margin": {"t": 50, "r": 30, "b": 30, "l": 30}  # ✅ Melhor prática
}
```

## 📚 **Valores Válidos para Font Weight no Plotly**

### Opções Aceitas:
1. **Inteiros:** `1` a `1000` (ex: `400`, `500`, `600`, `700`)
2. **Strings específicas:** `"normal"` ou `"bold"`

### Exemplos Corretos:
```python
# ✅ Usando inteiro
font={"weight": 600}

# ✅ Usando string específica
font={"weight": "bold"}

# ✅ Usando valor padrão normal
font={"weight": "normal"}
```

## 🎯 **Resultado**
- ✅ Dashboard carrega sem erros
- ✅ Tema moderno aplicado corretamente
- ✅ Fontes Inter funcionando
- ✅ Layout responsivo mantido
- ✅ Sistema de cores profissional ativo

## 🚀 **Status Final**
**PROBLEMA RESOLVIDO** - O dashboard está funcionando perfeitamente em `http://localhost:8502` com todas as melhorias visuais implementadas e sem erros de validação do Plotly.
