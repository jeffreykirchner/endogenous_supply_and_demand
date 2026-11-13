import logging

from asgiref.sync import sync_to_async

from django.core.exceptions import ObjectDoesNotExist

from main.models import Session
from main.models import ParameterSetSupplier

from main.forms import ParameterSetSupplierForm

from ..session_parameters_consumer_mixins.get_parameter_set import take_get_parameter_set

import main

class ParameterSetSuppliersMixin():
    '''
    parameter set plaeyer mixin
    '''

    async def update_parameter_set_supplier(self, event):
        '''
        update a parameterset supplier
        '''

        message_data = {}
        message_data["status"] = await take_update_parameter_set_supplier(event["message_text"])
        message_data["parameter_set"] = await take_get_parameter_set(event["message_text"]["session_id"])

        await self.send_message(message_to_self=message_data, message_to_group=None,
                                message_type="update_parameter_set", send_to_client=True, send_to_group=False)

    async def remove_parameterset_supplier(self, event):
        '''
        remove a parameterset supplier
        '''

        message_data = {}
        message_data["status"] = await take_remove_parameterset_supplier(event["message_text"])
        message_data["parameter_set"] = await take_get_parameter_set(event["message_text"]["session_id"])

        await self.send_message(message_to_self=message_data, message_to_group=None,
                                message_type="update_parameter_set", send_to_client=True, send_to_group=False)
    
    async def add_parameterset_supplier(self, event):
        '''
        add a parameterset supplier
        '''

        message_data = {}
        message_data["status"] = await take_add_parameterset_supplier(event["message_text"])
        message_data["parameter_set"] = await take_get_parameter_set(event["message_text"]["session_id"])

        await self.send_message(message_to_self=message_data, message_to_group=None,
                                message_type="update_parameter_set", send_to_client=True, send_to_group=False)

    async def duplicate_parameterset_supplier(self, event):
        '''
        duplicate a parameterset supplier
        '''

        message_data = {}
        message_data["status"] = await take_duplicate_parameterset_supplier(event["message_text"])
        message_data["parameter_set"] = await take_get_parameter_set(event["message_text"]["session_id"])

        await self.send_message(message_to_self=message_data, message_to_group=None,
                                message_type="update_parameter_set", send_to_client=True, send_to_group=False)

@sync_to_async
def take_update_parameter_set_supplier(data):
    '''
    update parameterset supplier
    '''   
    logger = logging.getLogger(__name__) 
    # logger.info(f"Update parameterset supplier: {data}")

    session_id = data["session_id"]
    parameterset_supplier_id = data["parameterset_supplier_id"]
    form_data = data["form_data"]

    try:        
        parameter_set_supplier = ParameterSetSupplier.objects.get(id=parameterset_supplier_id)
    except ObjectDoesNotExist:
        logger.warning(f"take_update_parameter_set_supplier parameterset_supplier, not found ID: {parameterset_supplier_id}")
        return
    
    form_data_dict = form_data

    # logger.info(f'form_data_dict : {form_data_dict}')

    form = ParameterSetSupplierForm(form_data_dict, instance=parameter_set_supplier)

    if form.is_valid():         
        form.save()              
        parameter_set_supplier.parameter_set.update_json_fk(update_suppliers=True)

        return {"value" : "success"}                      
                                
    logger.warning("Invalid parameterset supplier form")
    return {"value" : "fail", "errors" : dict(form.errors.items())}

@sync_to_async
def take_remove_parameterset_supplier(data):
    '''
    remove the specifed parmeterset supplier
    '''
    logger = logging.getLogger(__name__) 
    # logger.info(f"Remove parameterset supplier: {data}")

    session_id = data["session_id"]
    parameterset_supplier_id = data["parameterset_supplier_id"]

    try:        
        session = Session.objects.get(id=session_id)
        parameter_set_supplier = ParameterSetSupplier.objects.get(id=parameterset_supplier_id)
        
    except ObjectDoesNotExist:
        logger.warning(f"take_remove_parameterset_supplier, not found ID: {parameterset_supplier_id}")
        return
    
    parameter_set_supplier.delete()
    session.parameter_set.update_json_fk(update_suppliers=True)
    
    return {"value" : "success"}

@sync_to_async
def take_add_parameterset_supplier(data):
    '''
    add a new parameter supplier to the parameter set
    '''
    logger = logging.getLogger(__name__) 
    # logger.info(f"Add parameterset supplier: {data}")

    session_id = data["session_id"]

    try:        
        session = Session.objects.get(id=session_id)
    except ObjectDoesNotExist:
        logger.warning(f"take_add_parameterset_supplier session, not found ID: {session_id}")
        return {"value" : "fail"}

    parameter_set_supplier = ParameterSetSupplier.objects.create(parameter_set=session.parameter_set)
    session.parameter_set.update_json_fk(update_suppliers=True)

    return {"value" : "success"}

@sync_to_async
def take_duplicate_parameterset_supplier(data):
    '''
    duplicate parameter supplier to the parameter set
    '''
    logger = logging.getLogger(__name__) 
    # logger.info(f"Add parameterset supplier: {data}")

    session_id = data["session_id"]

    try:        
        session = Session.objects.get(id=session_id)
        parameter_set = session.parameter_set
    except ObjectDoesNotExist:
        logger.warning(f"take_update_take_update_parameter_set supplier, not found ID: {session_id}")
        return {"value" : "fail"}
    
    parameter_set_supplier_source = ParameterSetSupplier.objects.get(id=data["parameterset_supplier_id"])

    parameter_set_supplier = main.models.ParameterSetSupplier()
    parameter_set_supplier.parameter_set = parameter_set
    
    parameter_set_supplier.from_dict(parameter_set_supplier_source.json())

    parameter_set.update_json_fk(update_suppliers=True)
    
    return {"value" : "success"}
