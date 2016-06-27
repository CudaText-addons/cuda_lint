import cudatext as app
import cuda_lint_options as opt

def do_options_dlg():
    c1 = chr(1)
    text = '\n'.join([] 
        +[c1.join(['type=button', 'pos=6,6,180,0', 'cap=Color of errors'])]
        +[c1.join(['type=check', 'pos=186,6,400,0', 'cap=Colored error bookmarks'])]
        +[c1.join(['type=button', 'pos=6,36,180,0', 'cap=Color of warns'])]
        +[c1.join(['type=check', 'pos=186,36,400,0', 'cap=Colored warn bookmarks'])]
        +[c1.join(['type=button', 'pos=6,66,180,0', 'cap=Color of infos'])]
        +[c1.join(['type=check', 'pos=186,66,400,0', 'cap=Colored info bookmarks'])]
        +[c1.join(['type=check', 'pos=6,100,400,0', 'cap=Do linting on opening file'])]
        +[c1.join(['type=check', 'pos=6,126,400,0', 'cap=Do linting after text changed'])]
        +[c1.join(['type=button', 'pos=206,156,300,0', 'cap=OK'])]
        +[c1.join(['type=button', 'pos=306,156,400,0', 'cap=Cancel'])]
        )
    res = app.dlg_custom('CudaLint options', 406, 190, text)
    if res is None: return
    
    btn, text = res
    