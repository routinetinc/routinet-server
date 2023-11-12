from drf_yasg.utils import swagger_auto_schema
from routine import serializers
from drf_yasg import openapi

class decorators():
    routine_post_schema = swagger_auto_schema(
            operation_summary="新規ルーティンを作成する",  # オペレーションの要約
            operation_description="ルーティン情報を受け取り、新規ルーティンをDBに登録する。ルーティン登録が完了するとそのＩＤを返す。\n\
                requestのstart_timeとend_timeは'HHMMSS+TZ'の形式\n\
                requestのdowは['0', '1', '2']のような形を想定。 // 月曜を '0' とし連番で定義。",  # オペレーションの説明
            responses={
                200: openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'data': openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                'routine_id': openapi.Schema(type=openapi.TYPE_INTEGER),
                            },
                        )
                    }
                )
            },  # レスポンスの詳細
            request_body=serializers.Routine_create,  # リクエストの詳細
        )
    
    routine_patch_schema = swagger_auto_schema(
            operation_summary="既存ルーティンを編集する",  # オペレーションの要約
            operation_description="ルーティン情報を受け取り、既存ルーティンの変更をDBに登録する。ルーティン情報が変更分のみの場合、その属性を更新する。返り値としてルーティンIDを返す。\n\
                requestのstart_timeとend_timeは'HHMMSS+TZ'の形式\n\
                requestのdowは['0', '1', '2']のような形を想定。 // 月曜を '0' とし連番で定義。",  # オペレーションの説明
            responses={
                200: openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'data': openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                'routine_id': openapi.Schema(type=openapi.TYPE_INTEGER),
                            },
                        )
                    }
                )
            },  # レスポンスの詳細
            request_body=serializers.Routine_update,  # リクエストの詳細
        )
    
    routine_delete_schema = swagger_auto_schema(
            operation_summary="既存ルーティンを削除する",  # オペレーションの要約
            operation_description="ルーティン情報を受け取り、ルーティン削除をDBに登録する。返り値としてルーティンIDを返す。",  # オペレーションの説明
            responses={
                200: openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'data': openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                'routine_id': openapi.Schema(type=openapi.TYPE_INTEGER),
                            },
                        )
                    }
                )
            },  # レスポンスの詳細
            request_body=serializers.Routine_delete,  # リクエストの詳細
        )
    
    readroutineandtask_get_schema = swagger_auto_schema(
        operation_summary="ホーム画面表示：ルーティン、タスクを取得",  # オペレーションの要約
            operation_description="ログインユーザーの、一週間分のルーティーンとタスクを取得する。\n\
                どの一週間を取得するのかを指定するのにクエリパラメータを用いる。取得する週の月曜日の日付をISO形式で指定する。\n\
                例：2023-10-23から2023-10-29の一週間分を取得したい際はweek_startを20231023にする。\n\
                responseのmon,tueなどのidは時系列\n\
                consecutive_daysは連続達成日数\n\
                required_timeの単位は秒\n\
                required_timeがnullの時は、リアルタイムタスクでない時",  # オペレーションの説明
            responses={
                200: openapi.Schema(
            type=openapi.TYPE_OBJECT,
        properties={
            "status_code": openapi.Schema(type=openapi.TYPE_INTEGER),
            "data": openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "mon": openapi.Schema(
                        type=openapi.TYPE_ARRAY,
                        items=openapi.Schema(type=openapi.TYPE_STRING),
                    ),
                    "tue": openapi.Schema(
                        type=openapi.TYPE_ARRAY,
                        items=openapi.Schema(type=openapi.TYPE_STRING),
                    ),
                    # 同様にwed, thu, fri, sat, sunの定義を続けます。
                    "wed": openapi.Schema(
                        type=openapi.TYPE_ARRAY,
                        items=openapi.Schema(type=openapi.TYPE_STRING),
                    ),
                    "thu": openapi.Schema(
                        type=openapi.TYPE_ARRAY,
                        items=openapi.Schema(type=openapi.TYPE_STRING),
                    ),
                    "fri": openapi.Schema(
                        type=openapi.TYPE_ARRAY,
                        items=openapi.Schema(type=openapi.TYPE_STRING),
                    ),
                    "sat": openapi.Schema(
                        type=openapi.TYPE_ARRAY,
                        items=openapi.Schema(type=openapi.TYPE_STRING),
                    ),
                    "sun": openapi.Schema(
                        type=openapi.TYPE_ARRAY,
                        items=openapi.Schema(type=openapi.TYPE_STRING),
                    ),
                    "routines": openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        additional_properties=openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                "start_time": openapi.Schema(type=openapi.TYPE_STRING),
                                "end_time": openapi.Schema(type=openapi.TYPE_STRING),
                                "title": openapi.Schema(type=openapi.TYPE_STRING),
                                "tag_name": openapi.Schema(type=openapi.TYPE_STRING),
                                "real_time": openapi.Schema(type=openapi.TYPE_BOOLEAN),
                                "consecutive_days": openapi.Schema(type=openapi.TYPE_INTEGER),
                                "tasks": openapi.Schema(
                                    type=openapi.TYPE_ARRAY,
                                    items=openapi.Schema(
                                        type=openapi.TYPE_OBJECT,
                                        properties={
                                            "task_id": openapi.Schema(type=openapi.TYPE_STRING),
                                            "title": openapi.Schema(type=openapi.TYPE_STRING),
                                            "detail": openapi.Schema(type=openapi.TYPE_STRING),
                                            "required_time": openapi.Schema(type=openapi.TYPE_INTEGER, nullable=True),
                                            "is_achieved": openapi.Schema(type=openapi.TYPE_BOOLEAN),
                                        }
                                    )
                                )
                            }
                        )
                    ),
                }
            )
        })})