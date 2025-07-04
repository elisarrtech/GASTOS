def colorear_estado(val):
    if val == "PAGADO":
        return 'background-color: #d4edda; color: #155724; text-align: center'
    elif val == "NO PAGADO":
        return 'background-color: #f8d7da; color: #721c24; text-align: center'
    else:
        return ''
