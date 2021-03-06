import unittest.mock

import monstro.testing

from monstro import forms, db


class TestForm(forms.Form):

    string = forms.String(
        label='Label', help_text='Help', default='default', read_only=True
    )
    number = forms.Integer()


class TestModel(db.Model):

    string = db.String(default='default')
    number = db.Integer()

    class Meta:
        collection = 'test'

    async def validate(self):
        await super().validate()

        if self.string == 'random':
            self.string = '42'


class TestModelForm(forms.ModelForm):

    float = db.Float()

    class Meta:
        model = TestModel
        fields = ('string',)


class FormTest(monstro.testing.AsyncTestCase):

    def test_new(self):
        self.assertIsInstance(TestForm.Meta.fields['string'], forms.String)
        self.assertIsInstance(TestForm.Meta.fields['number'], forms.Integer)

    async def test_validate(self):
        instance = TestForm(data={'number': '1'})

        await instance.validate()

        self.assertEqual(instance.data['number'], 1)

    async def test_validate__error(self):
        instance = TestForm(data={'string': 1})

        with self.assertRaises(forms.ValidationError) as context:
            await instance.validate()

        self.assertIn('string', context.exception.error)
        self.assertIn('string', instance.errors)

    async def test_get_options(self):
        self.assertEqual(
            {
                'name': 'string',
                'label': 'Label',
                'help_text': 'Help',
                'required': False,
                'read_only': True,
                'default': 'default',
                'widget': {
                    'attrs': {'type': 'text'},
                    'tag': 'input',
                }
            }, (await TestForm.get_options())[0]
        )

    async def test_is_valid(self):
        instance = TestForm(data={'string': 1})

        self.assertFalse(await instance.is_valid())

    async def test_is_valid__exception(self):
        error = {'number': 'Error'}

        async def mock(self):
            raise self.ValidationError(error)
        mock.target = 'monstro.forms.forms.Form.validate'

        instance = TestForm(data={'number': '1'})

        with unittest.mock.patch(mock.target, mock):
            self.assertFalse(await instance.is_valid())

        self.assertEqual(error, instance.errors)

    async def test_is_valid__exception_string(self):

        async def mock(self):
            raise self.ValidationError('string')
        mock.target = 'monstro.forms.forms.Form.validate'

        instance = TestForm(data={'number': '1'})

        with unittest.mock.patch(mock.target, mock):
            self.assertFalse(await instance.is_valid())

        self.assertEqual({'common': 'string'}, instance.errors)


class ModelFormTest(monstro.testing.AsyncTestCase):

    def test_new(self):
        self.assertEqual(
            TestModelForm.Meta.fields['string'],  # pylint:disable=E1126
            TestModel.Meta.fields['string']
        )

        self.assertNotIn('number', TestModelForm.Meta.fields)
        self.assertIsInstance(TestModelForm.Meta.fields['float'], db.Float)  # pylint:disable=E1126

    async def test_validate__read_only(self):
        TestModelForm.Meta.fields['string'].read_only = True  # pylint:disable=E1126
        instance = TestModelForm(data={'float': '1', 'string': 'value'})

        await instance.validate()

        self.assertEqual(
            instance.data['string'],
            TestForm.Meta.fields['string'].default
        )

    async def test_save__model_validate_call(self):
        instance = TestModelForm(
            instance=TestModel(string='test', number=1),
            data={'float': '1', 'string': 'random'}
        )

        await instance.save()

        self.assertEqual('42', (await instance.serialize())['string'])
