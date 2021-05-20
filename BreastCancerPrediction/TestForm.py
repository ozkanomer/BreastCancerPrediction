from wtforms import Form, StringField, IntegerField, FloatField, SelectField

# Data Entry Form with WTF Form
class TestForm(Form):
    symptom = SelectField(u'Patient Symptoms', choices=[('None', 'None'),('Routine Control', 'Routine Control'), ('Lump', 'Lump or area that feels thicker'), ('Orange', 'Like the skin of an orange'), ('Redness', 'Redness around the nipple'), ('Nipple Size', 'Nipple has become pulled in or change its position'), ('Breast Shape', 'A change in size or shape of the breast'), ('Liquid Come', 'Liquid comes from the nipple without squeezing'), ('Pain', 'Pain in breast'), ('Bloody Discharge', 'Bloody discharge'), ('Texture Change', 'Texture change'), ('Color Change', 'Color Change')])
    Clump_Thickness = FloatField("Clump Thickness")
    uCell_Size = FloatField("Uniformity of Cell Size")
    Cell_Shape = FloatField("Uniformity of Cell Shape")
    Adhesion = FloatField("Marginal Adhesion")
    sCell_Size = FloatField("Single Epithelial Cell Size")
    Bare_Nuclei = FloatField("Bare Nuclei")
    Bland_Chromatin = FloatField("Bland Chromatin")
    Normal_Nucleoli = FloatField("Normal Nucleoli")
    Mitoses = FloatField("Mitoses")