from drf_yasg.utils import swagger_auto_schema
from routine import serializers
from drf_yasg import openapi

class decorators():
    routine_get_schema = swagger_auto_schema(
        operation_summary="ルーティン情報取得",
        operation_description="指定したルーティンIDに基づいて、ルーティン情報および関連するタスク情報を取得する。",
        manual_parameters=[
            openapi.Parameter(
                name='routine_id',
                in_=openapi.IN_QUERY,
                description='ルーティンID',
                type=openapi.TYPE_STRING,
                required=True
            )
        ],
        responses={
            200: openapi.Response(
                description="Successful Response",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'status_code': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'data': openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                'routine_id': openapi.Schema(type=openapi.TYPE_STRING),
                                'start_time': openapi.Schema(type=openapi.TYPE_STRING),
                                'end_time': openapi.Schema(type=openapi.TYPE_STRING),
                                'title': openapi.Schema(type=openapi.TYPE_STRING),
                                'tag_name': openapi.Schema(type=openapi.TYPE_STRING),
                                'real_time': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                                'consecutive_days': openapi.Schema(type=openapi.TYPE_INTEGER),
                                'dow': openapi.Schema(
                                    type=openapi.TYPE_ARRAY,
                                    items=openapi.Schema(type=openapi.TYPE_STRING)
                                ),
                                'tasks': openapi.Schema(
                                    type=openapi.TYPE_ARRAY,
                                    items=openapi.Schema(
                                        type=openapi.TYPE_OBJECT,
                                        properties={
                                            'task_id': openapi.Schema(type=openapi.TYPE_STRING),
                                            'title': openapi.Schema(type=openapi.TYPE_STRING),
                                            'detail': openapi.Schema(type=openapi.TYPE_STRING),
                                            'required_time': openapi.Schema(type=openapi.TYPE_INTEGER),
                                            'is_achieved': openapi.Schema(type=openapi.TYPE_BOOLEAN)
                                        }
                                    )
                                )
                            }
                        )
                    }
                )
            )
        }
    )

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
    

    routine_finish_create_post_schema = swagger_auto_schema(
        operation_summary="ルーティンの完了",
        operation_description="アイコン、メモの内容と共にルーティン完了を登録する。返り値として、Done2で表示するルーティン連続達成日数やタスクごとにかかった時間が返る。",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'data': openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'routine_id': openapi.Schema(type=openapi.TYPE_STRING),
                        'icon': openapi.Schema(type=openapi.TYPE_STRING),
                        'memo': openapi.Schema(type=openapi.TYPE_STRING)
                    },
                    required=['routine_id', 'icon', 'memo']
                )
            }
        ),
        responses={
            200: openapi.Response(
                description="Successful Response",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'status_code': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'data': openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                'routine_finish_id': openapi.Schema(type=openapi.TYPE_STRING),
                                'consecutive_days': openapi.Schema(type=openapi.TYPE_INTEGER),
                                'tasks': openapi.Schema(
                                    type=openapi.TYPE_ARRAY,
                                    items=openapi.Schema(
                                        type=openapi.TYPE_OBJECT,
                                        properties={
                                            'task_name': openapi.Schema(type=openapi.TYPE_STRING),
                                            'done_time': openapi.Schema(type=openapi.TYPE_INTEGER)
                                        }
                                    )
                                )
                            }
                        )
                    }
                )
            ),
            # You can add other status codes and responses as needed
        }
    )

    routine_finish_create_patch_schema = swagger_auto_schema(
        operation_summary="ルーティン完了記録の更新",
        operation_description="指定したルーティン完了記録を更新する。例えば、アイコンやメモを変更することができる。",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'routine_finish_id': openapi.Schema(type=openapi.TYPE_STRING, description="ルーティン完了ID"),
                'icon': openapi.Schema(type=openapi.TYPE_STRING, description="更新するアイコン", nullable=True),
                'memo': openapi.Schema(type=openapi.TYPE_STRING, description="更新するメモ", nullable=True)
            },
            required=['routine_finish_id']
        ),
        responses={
            200: openapi.Response(
                description="Successful Response",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'status_code': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'message': openapi.Schema(type=openapi.TYPE_STRING, description="更新成功のメッセージ")
                    }
                )
            ),
            400: 'Bad Request',
            404: 'Not Found'
            # You can add other status codes and responses as needed
        }
    )

    task_post_schema = swagger_auto_schema(
        operation_summary="タスク作成",
        operation_description="新規のタスクを作成する。返り値としてタスクIDを返す。",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'data': openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'routine_id': openapi.Schema(type=openapi.TYPE_INTEGER, description="ルーティンID"),
                        'title': openapi.Schema(type=openapi.TYPE_STRING, description="タスクのタイトル"),
                        'detail': openapi.Schema(type=openapi.TYPE_STRING, description="タスクの詳細"),
                        'icon': openapi.Schema(type=openapi.TYPE_STRING, description="タスクのアイコン"),
                        'required_time': openapi.Schema(type=openapi.TYPE_INTEGER, description="タスクに必要な時間（秒）")
                    },
                    required=['routine_id', 'title', 'detail', 'icon', 'required_time']
                )
            }
        ),
        responses={
            200: openapi.Response(
                description="Successful Response",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'status_code': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'data': openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                'task_id': openapi.Schema(type=openapi.TYPE_STRING, description="作成されたタスクのID")
                            }
                        )
                    }
                )
            ),
            400: 'Bad Request',
            404: 'Not Found'
            # You can add other status codes and responses as needed
        }
    )

    task_patch_schema = swagger_auto_schema(
        operation_summary="タスク編集",
        operation_description="既存のタスクを編集する。返り値としてタスクIDを返す。",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'data': openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'task_id': openapi.Schema(type=openapi.TYPE_STRING, description="編集するタスクのID"),
                        'title': openapi.Schema(type=openapi.TYPE_STRING, description="タスクの新しいタイトル", nullable=True),
                        'detail': openapi.Schema(type=openapi.TYPE_STRING, description="タスクの新しい詳細", nullable=True),
                        'icon': openapi.Schema(type=openapi.TYPE_STRING, description="タスクの新しいアイコン", nullable=True),
                        'required_time': openapi.Schema(type=openapi.TYPE_INTEGER, description="タスクに必要な新しい時間（秒）", nullable=True)
                    },
                    required=['task_id']
                )
            }
        ),
        responses={
            200: openapi.Response(
                description="Successful Response",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'status_code': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'data': openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                'task_id': openapi.Schema(type=openapi.TYPE_STRING, description="更新されたタスクのID")
                            }
                        )
                    }
                )
            ),
            400: 'Bad Request',
            404: 'Task Not Found'
            # You can add other status codes and responses as needed
        }
    )

    task_delete_schema = swagger_auto_schema(
        operation_summary="タスク削除",
        operation_description="指定されたタスクIDのタスクを削除する。成功した場合、削除されたタスクのIDを返す。",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'data': openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'task_id': openapi.Schema(type=openapi.TYPE_STRING, description="削除するタスクのID")
                    },
                    required=['task_id']
                )
            }
        ),
        responses={
            200: openapi.Response(
                description="Successful Response",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'status_code': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'data': openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                'task_id': openapi.Schema(type=openapi.TYPE_STRING, description="削除されたタスクのID")
                            }
                        )
                    }
                )
            ),
            400: 'Bad Request',
            404: 'Task Not Found'
            # You can add other status codes and responses as needed
        }
    )

    no_available_task_post_schema = swagger_auto_schema(
        operation_summary="タスクの完了",
        operation_description="指定されたタスクIDのタスク完了を登録する。返り値としてタスク完了IDを返す。",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'data': openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'task_id': openapi.Schema(type=openapi.TYPE_STRING, description="完了するタスクのID"),
                        'done_time': openapi.Schema(type=openapi.TYPE_INTEGER, description="タスクにかかった時間（秒）。リアルタイムタスクでない場合はnull", nullable=True)
                    },
                    required=['task_id']
                )
            }
        ),
        responses={
            200: openapi.Response(
                description="Successful Response",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'status_code': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'data': openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                'task_finish_id': openapi.Schema(type=openapi.TYPE_STRING, description="登録されたタスク完了のID")
                            }
                        )
                    }
                )
            ),
            400: 'Bad Request',
            404: 'Task Not Found'
            # You can add other status codes and responses as needed
        }
    )

    timetree_before_post_schema = swagger_auto_schema(
        operation_summary="ある日の前7日間のTimeTree取得",
        operation_description="指定された日付の前7日間のTimeTreeを取得する。",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'data': openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'day': openapi.Schema(type=openapi.TYPE_STRING, description="基準となる日付"),
                        'routine_id': openapi.Schema(type=openapi.TYPE_STRING, description="ルーティンID")
                    },
                    required=['day', 'routine_id']
                )
            }
        ),
        responses={
            200: openapi.Response(
                description="Successful Response",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'status_code': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'data': openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                'timetree': openapi.Schema(
                                    type=openapi.TYPE_OBJECT,
                                    properties={
                                        'routine_id': openapi.Schema(type=openapi.TYPE_STRING),
                                        'days': openapi.Schema(
                                            type=openapi.TYPE_ARRAY,
                                            items=openapi.Schema(
                                                type=openapi.TYPE_OBJECT,
                                                properties={
                                                    'day': openapi.Schema(type=openapi.TYPE_STRING),
                                                    'tasks': openapi.Schema(
                                                        type=openapi.TYPE_ARRAY,
                                                        items=openapi.Schema(
                                                            type=openapi.TYPE_OBJECT,
                                                            properties={
                                                                'task_finish_id': openapi.Schema(type=openapi.TYPE_STRING),
                                                                'finish_time': openapi.Schema(type=openapi.TYPE_STRING),
                                                                'doing_time': openapi.Schema(type=openapi.TYPE_INTEGER, nullable=True),
                                                                'comment': openapi.Schema(type=openapi.TYPE_STRING, nullable=True)
                                                            }
                                                        )
                                                    )
                                                }
                                            )
                                        )
                                    }
                                )
                            }
                        )
                    }
                )
            ),
            400: 'Bad Request'
            # You can add other status codes and responses as needed
        }
    )
    
    timetree_aftertobefore_post_schema = swagger_auto_schema(
        operation_summary="ある日の前後7日間のTimeTree取得",
        operation_description="指定された日付の前後7日間のTimeTreeを取得する。",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'data': openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'day': openapi.Schema(type=openapi.TYPE_STRING, description="基準となる日付"),
                        'routine_id': openapi.Schema(type=openapi.TYPE_STRING, description="ルーティンID")
                    },
                    required=['day', 'routine_id']
                )
            }
        ),
        responses={
            200: openapi.Response(
                description="Successful Response",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'status_code': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'data': openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                'timetree': openapi.Schema(
                                    type=openapi.TYPE_ARRAY,
                                    items=openapi.Schema(
                                        type=openapi.TYPE_OBJECT,
                                        properties={
                                            'day': openapi.Schema(type=openapi.TYPE_STRING),
                                            'tasks': openapi.Schema(
                                                type=openapi.TYPE_ARRAY,
                                                items=openapi.Schema(
                                                    type=openapi.TYPE_OBJECT,
                                                    properties={
                                                        'task_finish_id': openapi.Schema(type=openapi.TYPE_STRING),
                                                        'finish_time': openapi.Schema(type=openapi.TYPE_STRING),
                                                        'doing_time': openapi.Schema(type=openapi.TYPE_INTEGER, nullable=True),
                                                        'comment': openapi.Schema(type=openapi.TYPE_STRING, nullable=True)
                                                    }
                                                )
                                            )
                                        }
                                    )
                                )
                            }
                        )
                    }
                )
            ),
            400: 'Bad Request'
            # You can add other status codes and responses as needed
        }
    )

    timetree_after_post_schema = swagger_auto_schema(
        operation_summary="ある日の後7日間のTimeTree取得",
        operation_description="指定された日付の後7日間のTimeTreeを取得する。",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'data': openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'day': openapi.Schema(type=openapi.TYPE_STRING, description="基準となる日付"),
                        'routine_id': openapi.Schema(type=openapi.TYPE_STRING, description="ルーティンID")
                    },
                    required=['day', 'routine_id']
                )
            }
        ),
        responses={
            200: openapi.Response(
                description="Successful Response",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'status_code': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'data': openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                'timetree': openapi.Schema(
                                    type=openapi.TYPE_ARRAY,
                                    items=openapi.Schema(
                                        type=openapi.TYPE_OBJECT,
                                        properties={
                                            'day': openapi.Schema(type=openapi.TYPE_STRING),
                                            'tasks': openapi.Schema(
                                                type=openapi.TYPE_ARRAY,
                                                items=openapi.Schema(
                                                    type=openapi.TYPE_OBJECT,
                                                    properties={
                                                        'task_finish_id': openapi.Schema(type=openapi.TYPE_STRING),
                                                        'finish_time': openapi.Schema(type=openapi.TYPE_STRING),
                                                        'doing_time': openapi.Schema(type=openapi.TYPE_INTEGER, nullable=True),
                                                        'comment': openapi.Schema(type=openapi.TYPE_STRING, nullable=True)
                                                    }
                                                )
                                            )
                                        }
                                    )
                                )
                            }
                        )
                    }
                )
            ),
            400: 'Bad Request'
            # You can add other status codes and responses as needed
        }
    )