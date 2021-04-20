import simple_history
from modeltranslation import translator

from .models import Answer, Question, QuestionCategory, QuestionContext


@translator.register(QuestionContext)
class QuestionContextTranslationOptions(translator.TranslationOptions):
    fields = ("title",)


@translator.register(QuestionCategory)
class QuestionCategoryTranslationOptions(translator.TranslationOptions):
    fields = ("title",)


@translator.register(Question)
class QuestionTranslationOptions(translator.TranslationOptions):
    fields = ("title", "hints")


@translator.register(Answer)
class AnswerTranslationOptions(translator.TranslationOptions):
    fields = ("title",)


simple_history.register(QuestionContext)
simple_history.register(QuestionCategory)
simple_history.register(Question)
simple_history.register(Answer)
