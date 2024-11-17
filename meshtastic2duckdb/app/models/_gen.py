from fastapi import FastAPI, status, Request, Response, Path

from ._message    import MessageClass, Message
from ._base       import SharedFilterQuery, TimedFilterQuery
from ..dbgenerics import GenericSession, GenericSessionManager, DbEngine



async def api_model_get( model: Message,      session_manager: GenericSessionManager, request: Request, response: Response, query_filter: SharedFilterQuery ) -> list[Message]:
	#print("api_model_get", "model", model, "session_manager", session_manager, "request", request, "response", response, "query_filter", query_filter)
	#https://fastapi.tiangolo.com/tutorial/sql-databases/#read-heroes

	resp = model.Query(session_manager=session_manager, query_filter=query_filter)

	return resp



async def api_model_post( data: MessageClass, session_manager: GenericSessionManager, request: Request, response: Response ) -> None:
	#print("api_model_post", "data", data, type(data), "session_manager", session_manager, "request", request, "response", response)
	#print(dir(data))

	orm = data.toORM()
	#orm = models.class_to_ORM(data)
	# print("  orm", orm)

	with session_manager as session:
		session.add(orm)
		session.commit()
	# print("  STORED")

	return None



def gen_endpoint(*, app: FastAPI, verb: str, endpoint: str, name: str, summary: str, description: str, model: Message, session_manager_t, tags: list[str], filter_key:str=None, filter_is_list: bool=False, response_model=None, fixed_response=None, status_code=None):
	assert verb in ("GET","POST")
	alias        = None
	data_class   = model.__dataclass__()
	query_filter = model.__filter__()

	operation_id = f"{endpoint}_{verb}".lower().replace("/","_").replace("{","_").replace("}","_").replace(":","_").replace("-","_").replace("__","_").strip("_")
	#print(f"  operation_id {operation_id}")

	if "{" in endpoint:
		alias = endpoint.split("{")[1].split("}")[0]
		#print(f"  ALIAS {alias}")

	if fixed_response is not None:
		assert verb == "GET"

	def mod_filter_key(filter_query, filter_key:str, filter_is_list:bool, path_param: str):
		if filter_key is not None:
			assert hasattr(filter_query, filter_key), f"query_filter '{query_filter}' does not have filter_key '{filter_key}': {dir(query_filter)}. {query_filter.model_fields}"

			if filter_is_list:
				setattr(filter_query, filter_key, [path_param])
			else:
				setattr(filter_query, filter_key,  path_param)

	if verb == "GET":
		if alias is not None:
			@app.get(
				endpoint,
				name           = name,
				summary        = summary,
				description    = description,
				tags           = tags,
				operation_id   = operation_id,
				response_model = response_model,
				status_code    = status_code
			)
			async def endpoint(                             session_manager: session_manager_t, request: Request, response: Response, query_filter: query_filter, path_param: str = Path(alias=alias)) -> response_model:
				if fixed_response:
					return fixed_response

				mod_filter_key(filter_query=query_filter, filter_key=filter_key, filter_is_list=filter_is_list, path_param=path_param)

				return await api_model_get(model=model, session_manager=session_manager,    request=request,  response=response, query_filter=query_filter)

		else:
			@app.get(
				endpoint,
				name           = name,
				summary        = summary,
				description    = description,
				tags           = tags,
				operation_id   = operation_id,
				response_model = response_model,
				status_code    = status_code
			)
			async def endpoint(                             session_manager: session_manager_t, request: Request, response: Response, query_filter: query_filter) -> response_model:
				if fixed_response:
					return fixed_response

				return await api_model_get(model=model, session_manager=session_manager,    request=request,  response=response, query_filter=query_filter)

	elif verb == "POST":
		if alias is not None:
			@app.post(
				endpoint,
				name           = name,
				summary        = summary,
				description    = description,
				tags           = tags,
				operation_id   = operation_id,
				response_model = response_model,
				status_code    = status_code
			)

			async def endpoint(                 data: data_class, session_manager: session_manager_t, request: Request, response: Response, query_filter: query_filter,  path_param: str = Path(alias=alias)) -> response_model:
				return await api_model_post(data=data  , session_manager=session_manager,    request=request,  response=response, path_param=path_param)

		else:
			@app.post(
				endpoint,
				name           = name,
				summary        = summary,
				description    = description,
				tags           = tags,
				operation_id   = operation_id,
				response_model = response_model,
				status_code    = status_code
			)

			async def endpoint(                 data: data_class, session_manager: session_manager_t, request: Request, response: Response, query_filter: query_filter) -> response_model:
				return await api_model_post(data=data  , session_manager=session_manager,    request=request,  response=response)

	return endpoint


