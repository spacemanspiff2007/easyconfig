**************************************
Class reference
**************************************

Models
======================================

ConfigModel
--------------------------------------

.. inheritance-diagram:: easyconfig.ConfigModel
   :top-classes: easyconfig.models.config_model.ConfigModel
   :parts: 1

.. autoclass:: easyconfig.ConfigModel
   :members: on_all_values_set, subscribe_for_changes
   :member-order: groupwise

PathModel
--------------------------------------

.. inheritance-diagram:: easyconfig.PathModel
   :top-classes: easyconfig.models.config_model.ConfigModel
   :parts: 1

.. autoclass:: easyconfig.PathModel
   :members: on_all_values_set, subscribe_for_changes, set_file_path
   :member-order: groupwise

AppConfig
--------------------------------------

.. inheritance-diagram:: easyconfig.AppConfig
   :top-classes: easyconfig.models.config_model.ConfigModel
   :parts: 1

.. autoclass:: easyconfig.AppConfig
   :members: on_all_values_set, subscribe_for_changes, set_file_path, load_dict, load_file
   :member-order: groupwise


Subscription
======================================

.. autoclass:: easyconfig.config_subscription.Subscription
   :members: cancel
