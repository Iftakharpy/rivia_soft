class Forms:
  CustomUser_repr_format = r"📨{fields.email} 👥{fields.first_name}"
 
  Selfassesment_type_repr_format = r"{fields.type_name}"
  Selfassemsent_tax_year_repr_format = r"📆 {fields.tax_year}"
  Selfassesment_client_id_repr_format = r"{'🔷'*{fields.client_rating}} 👥{fields.client_name} 📁{fields.client_file_number} 📞{fields.personal_phone_number} 📭{fields.personal_post_code}"

  Limited_client_id_repr_format = r"{'🔷'*{fields.client_rating}} 🏢{fields.client_name} 📂{fields.client_file_number} ☎{fields.director_phone_number} 📭{fields.director_post_code} ⓇⓃ{fields.company_reg_number}"



class HTML_Generator:
  CustomUser_repr_format = r"👥{first_name}"

  Selfassesment_type_repr_format = r"{type_name}"
  Selfassemsent_tax_year_repr_format = r"📆 {tax_year}"
  Selfassesment_client_id_repr_format = r"{'🔷'*{client_rating}} 👥{client_name} 📁{client_file_number} 📞{personal_phone_number} 📭{personal_post_code}"
  
  Limited_client_id_repr_format = r"{'🔷'*{client_rating}} 🏢{client_name} 📂{client_file_number}"
