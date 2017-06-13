from rest_framework.serializers import Serializer
from rest_framework.fields import IntegerField, CharField, URLField
from django.core.exceptions import ValidationError


# JsStackFrame = namedtuple('JsStackFrame', ['fileName', 
#                                            'functionName', 
#                                            'args', 
#                                            'lineNumber', 
#                                            'columnNumber'])


class StackFrameSerializer(Serializer):
    # https://github.com/stacktracejs/stackframe
    
    fileName = URLField(required=False)
    functionName = CharField(max_length=255, required=False)
    args = CharField(max_length=255, required=False)
    lineNumber = IntegerField(min_value=0,required=False)
    columnNumber = IntegerField(min_value=0,required=False)
    
#     def restore_object(self, attrs, instance=None):
#         return JsStackFrame(**attrs)
        

class LogEntrySerializer(Serializer):
    stack = StackFrameSerializer(many=True)
    
    def validate(self, attrs):
        if not attrs['stack']:
            raise ValidationError("No stack provided")
        return attrs
    
    