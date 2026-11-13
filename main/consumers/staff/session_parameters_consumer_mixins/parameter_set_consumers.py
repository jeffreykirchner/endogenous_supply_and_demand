import logging

from asgiref.sync import sync_to_async

from django.core.exceptions import ObjectDoesNotExist

from main.models import Session
from main.models import ParameterSetConsumer

from main.forms import ParameterSetConsumerForm

from ..session_parameters_consumer_mixins.get_parameter_set import take_get_parameter_set

import main

class ParameterSetConsumersMixin():
    '''
    parameter set consumers mixin
    '''

    async def update_parameter_set_consumer(self, event):
        '''
        update a parameterset consumer
        '''

        message_data = {}
        message_data["status"] = await take_update_parameter_set_consumer(event["message_text"])
        message_data["parameter_set"] = await take_get_parameter_set(event["message_text"]["session_id"])

        await self.send_message(message_to_self=message_data, message_to_group=None,
                                message_type="update_parameter_set", send_to_client=True, send_to_group=False)

    async def remove_parameterset_consumer(self, event):
        '''
        remove a parameterset consumer
        '''

        message_data = {}
        message_data["status"] = await take_remove_parameterset_consumer(event["message_text"])
        message_data["parameter_set"] = await take_get_parameter_set(event["message_text"]["session_id"])

        await self.send_message(message_to_self=message_data, message_to_group=None,
                                message_type="update_parameter_set", send_to_client=True, send_to_group=False)
    
    async def add_parameterset_consumer(self, event):
        '''
        add a parameterset consumer
        '''

        message_data = {}
        message_data["status"] = await take_add_parameterset_consumer(event["message_text"])
        message_data["parameter_set"] = await take_get_parameter_set(event["message_text"]["session_id"])

        await self.send_message(message_to_self=message_data, message_to_group=None,
                                message_type="update_parameter_set", send_to_client=True, send_to_group=False)

    async def duplicate_parameterset_consumer(self, event):
        '''
        duplicate a parameterset consumer
        '''

        message_data = {}
        message_data["status"] = await take_duplicate_parameterset_consumer(event["message_text"])
        message_data["parameter_set"] = await take_get_parameter_set(event["message_text"]["session_id"])

        await self.send_message(message_to_self=message_data, message_to_group=None,
                                message_type="update_parameter_set", send_to_client=True, send_to_group=False)

@sync_to_async
def take_update_parameter_set_consumer(data):
    '''
    update parameterset consumer
    '''   
    logger = logging.getLogger(__name__) 
    # logger.info(f"Update parameterset consumer: {data}")

    session_id = data["session_id"]
    parameterset_consumer_id = data["parameterset_consumer_id"]
    form_data = data["form_data"]

    try:        
        parameter_set_consumer = ParameterSetConsumer.objects.get(id=parameterset_consumer_id)
    except ObjectDoesNotExist:
        logger.warning(f"take_update_parameter_set_consumer parameterset_consumer, not found ID: {parameterset_consumer_id}")
        return
    
    form_data_dict = form_data

    # logger.info(f'form_data_dict : {form_data_dict}')

    form = ParameterSetConsumerForm(form_data_dict, instance=parameter_set_consumer)

    if form.is_valid():         
        form.save()              
        parameter_set_consumer.parameter_set.update_json_fk(update_consumers=True)

        return {"value" : "success"}                      
                                
    logger.warning("Invalid parameterset consumer form")
    return {"value" : "fail", "errors" : dict(form.errors.items())}

@sync_to_async
def take_remove_parameterset_consumer(data):
    '''
    remove the specifed parmeterset consumer
    '''
    logger = logging.getLogger(__name__) 
    # logger.info(f"Remove parameterset consumer: {data}")

    session_id = data["session_id"]
    parameterset_consumer_id = data["parameterset_consumer_id"]

    try:        
        session = Session.objects.get(id=session_id)
        parameter_set_consumer = ParameterSetConsumer.objects.get(id=parameterset_consumer_id)
        
    except ObjectDoesNotExist:
        logger.warning(f"take_remove_parameterset_consumer, not found ID: {parameterset_consumer_id}")
        return
    
    parameter_set_consumer.delete()
    session.parameter_set.update_json_fk(update_consumers=True)
    
    return {"value" : "success"}

@sync_to_async
def take_add_parameterset_consumer(data):
    '''
    add a new parameter consumer to the parameter set
    '''
    logger = logging.getLogger(__name__) 
    # logger.info(f"Add parameterset consumer: {data}")

    session_id = data["session_id"]

    try:        
        session = Session.objects.get(id=session_id)
    except ObjectDoesNotExist:
        logger.warning(f"take_add_parameterset_consumer session, not found ID: {session_id}")
        return {"value" : "fail"}

    parameter_set_consumer = ParameterSetConsumer.objects.create(parameter_set=session.parameter_set)
    session.parameter_set.update_json_fk(update_consumers=True)

    return {"value" : "success"}

@sync_to_async
def take_duplicate_parameterset_consumer(data):
    '''
    duplicate parameter consumer to the parameter set
    '''
    logger = logging.getLogger(__name__) 
    # logger.info(f"Add parameterset consumer: {data}")

    session_id = data["session_id"]

    try:        
        session = Session.objects.get(id=session_id)
        parameter_set = session.parameter_set
    except ObjectDoesNotExist:
        logger.warning(f"take_update_take_update_parameter_set consumer, not found ID: {session_id}")
        return {"value" : "fail"}
    
    parameter_set_consumer_source = ParameterSetConsumer.objects.get(id=data["parameterset_consumer_id"])

    parameter_set_consumer = main.models.ParameterSetConsumer()
    parameter_set_consumer.parameter_set = parameter_set
    
    parameter_set_consumer.from_dict(parameter_set_consumer_source.json())

    parameter_set.update_json_fk(update_consumers=True)
    
    return {"value" : "success"}
