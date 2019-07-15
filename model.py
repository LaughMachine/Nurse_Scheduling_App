from wtforms import Form, FloatField, validators, RadioField, SelectField, SubmitField, TextAreaField, DateField
from math import pi

class InputForm(Form):
    submit1 = SubmitField('test')
    sl = FloatField(
        label='Shift Length (hrs)', default=12)
    numnurse = FloatField(
        label='Number of Nurses Available: ', default=11,
        validators=[validators.InputRequired()])
    numnurse_2 = FloatField(
        label='Number of EDIN Nurses Available: ', default=4,
        validators=[validators.InputRequired()])
    nursetopat = FloatField(
        label='ntopat', default=5,
        validators=[validators.InputRequired()])
    nursetopat_2 = FloatField(
        label='ntopat_2', default=6,
        validators=[validators.InputRequired()])
    currnum1 = FloatField(
        label='Bay A', 
        validators=[validators.InputRequired()],
        description= 'Bay A')
    currnum2 = FloatField(
        label='Bay B', 
        validators=[validators.InputRequired()])
    currnum3 = FloatField(
        label='Bay C', 
        validators=[validators.InputRequired()])
    currnum4 = FloatField(
        label='Bay U', 
        validators=[validators.InputRequired()])
    currnum1_2 = FloatField(
        label='Bay A', 
        validators=[validators.InputRequired()],
        description= 'Bay A')
    currnum2_2 = FloatField(
        label='Bay B', 
        validators=[validators.InputRequired()])
    currnum3_2 = FloatField(
        label='Bay C', 
        validators=[validators.InputRequired()])
    dt = DateField(
        label='Pick a Date',
        format="%m/%d/%Y",
        validators=[validators.InputRequired()])

class InputForm_staffing_AM(Form):
    currnum1_0 = FloatField(
        label='Bay A',
        validators=[validators.InputRequired()],
        description= 'Bay A')
    currnum2_0 = FloatField(
        label='Bay B',
        validators=[validators.InputRequired()])
    currnum3_0 = FloatField(
        label='Bay C',
        validators=[validators.InputRequired()])
    currnum4_0 = FloatField(
        label='Bay U',
        validators=[validators.InputRequired()])
    currnum1_2_0 = FloatField(
        label='Bay A',
        validators=[validators.InputRequired()],
        description= 'Bay A')
    currnum2_2_0 = FloatField(
        label='Bay B',
        validators=[validators.InputRequired()])
    currnum3_2_0 = FloatField(
        label='Bay C',
        validators=[validators.InputRequired()])
    dt = DateField(
        label='Pick a Date',
        format="%m/%d/%Y",
        validators=[validators.InputRequired()])
    text = TextAreaField(u'Notes')

class InputForm_staffing_PM(Form):
    currnum1_0 = FloatField(
        label='Bay A',
        validators=[validators.InputRequired()],
        description= 'Bay A')
    currnum2_0 = FloatField(
        label='Bay B',
        validators=[validators.InputRequired()])
    currnum3_0 = FloatField(
        label='Bay C',
        validators=[validators.InputRequired()])
    currnum1_2_0 = FloatField(
        label='Bay A',
        validators=[validators.InputRequired()],
        description= 'Bay A')
    currnum2_2_0 = FloatField(
        label='Bay B',
        validators=[validators.InputRequired()])
    currnum3_2_0 = FloatField(
        label='Bay C',
        validators=[validators.InputRequired()])
    dt = DateField(
        label='Pick a Date',
        format="%m/%d/%Y",
        validators=[validators.InputRequired()])
    text = TextAreaField(u'Notes')

class InputForm_census_AM(Form):
    sl = FloatField(
        label='Shift Length (hrs)',
        default=12)
    numnurse = FloatField(
        label='Number of Nurses Available: ',
        default=11,
        validators=[validators.InputRequired()])
    numnurse_2 = FloatField(
        label='Number of EDIN Nurses Available: ',
        default=4,
        validators=[validators.InputRequired()])
    nursetopat = FloatField(
        label='ntopat', default=5,
        validators=[validators.InputRequired()])
    nursetopat_2 = FloatField(
        label='ntopat_2', default=6,
        validators=[validators.InputRequired()])
    currnum1 = FloatField(
        label='Bay A',
        validators=[validators.InputRequired()],
        description= 'Bay A')
    currnum2 = FloatField(
        label='Bay B',
        validators=[validators.InputRequired()])
    currnum3 = FloatField(
        label='Bay C',
        validators=[validators.InputRequired()])
    currnum4 = FloatField(
        label='Bay U',
        validators=[validators.InputRequired()])
    currnum1_2 = FloatField(
        label='Bay A',
        validators=[validators.InputRequired()],
        description= 'Bay A')
    currnum2_2 = FloatField(
        label='Bay B',
        validators=[validators.InputRequired()])
    currnum3_2 = FloatField(
        label='Bay C',
        validators=[validators.InputRequired()])
    dt = DateField(
        label='Pick a Date',
        format="%m/%d/%Y",
        validators=[validators.InputRequired()])

class InputForm_census_PM(Form):
    sl = FloatField(
        label='Shift Length (hrs)', default=12)
    numnurse = FloatField(
        label='Number of Nurses Available: ', default=11,
        validators=[validators.InputRequired()])
    numnurse_2 = FloatField(
        label='Number of EDIN Nurses Available: ', default=4,
        validators=[validators.InputRequired()])
    nursetopat = FloatField(
        label='ntopat', default=5,
        validators=[validators.InputRequired()])
    nursetopat_2 = FloatField(
        label='ntopat_2', default=6,
        validators=[validators.InputRequired()])
    currnum1 = FloatField(
        label='Bay A',
        validators=[validators.InputRequired()],
        description= 'Bay A')
    currnum2 = FloatField(
        label='Bay B',
        validators=[validators.InputRequired()])
    currnum3 = FloatField(
        label='Bay C',
        validators=[validators.InputRequired()])
    currnum1_2 = FloatField(
        label='Bay A',
        validators=[validators.InputRequired()],
        description= 'Bay A')
    currnum2_2 = FloatField(
        label='Bay B',
        validators=[validators.InputRequired()])
    currnum3_2 = FloatField(
        label='Bay C',
        validators=[validators.InputRequired()])
    dt = DateField(
        label='Pick a Date',
        format="%m/%d/%Y",
        validators=[validators.InputRequired()])