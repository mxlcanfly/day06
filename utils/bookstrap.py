class BootStrapForm:
    exculde_style_list = []

    def __init__(self,*args, **kwargs):
        super().__init__(*args, **kwargs)

        for name,field in self.fields.items():
            if name in self.exculde_style_list:
                continue
            field.widget.attrs['class'] = 'form-control'
            field.widget.attrs['placeholder'] = '请输入{}'.format(field.label)