json_data_xa = get_json_object('r_xa.json');
json_data_xa_m = get_json_object('xa_m.json');
json_data_xa_nm = get_json_object('xa_nm.json');

% disp(get_value(json_data_xa,'5100'));
% disp(get_value(json_data_xa_m,'5100'));
% disp(get_value(json_data_xa_nm,'5100'));
% disp(weight(json_data_xa_m,json_data_xa_nm,strcat('x','5100')));

% constant = get_constant_term(json_data_xa_m,json_data_xa_nm, json_data_xa);
% disp(constant)
% 
H = construct_H(json_data_xa_m,json_data_xa_nm, json_data_xa);
f_transpose = construct_f_transpose(json_data_xa_m,json_data_xa_nm, json_data_xa);
f = transpose(f_transpose);
n = length(f);
Aeq = zeros(0,n);
beq = zeros(0,1);
iA0 = false(n-1,1);

% A = []
A = zeros(n-1,n);
i = 1;
for k=1:n-1
    for j=1:n
        if(j==i)
            A(k,j) = 1;
        elseif(j==i+1)
            A(k,j) = -1;
        else
            A(k,j) = 0;
        end
        
    end
    i = i+1;
end
% disp(A);
b = zeros(n-1,1);
% disp(length(f_transpose));
opt = mpcActiveSetOptions;
[x,exitflag,iA,lambda] = mpcActiveSetSolver(H,f,A,b,Aeq,beq,iA0, opt);
disp(x);
% results = zeros(n,1);
% for k=1:n
%     results(k)= x(k) + constant;
% end
% 
% disp(results)

function w_xa = weight(json_data_xa_m,json_data_xa_nm,xa)
    w_xa = json_data_xa_m.(xa)+json_data_xa_nm.(xa);
end

function json_data = get_json_object(file_name)
    json_data = jsondecode(fileread(file_name));
end

function val = get_value(json_data, key)
    try
        val = json_data.(strcat('x',key));
    catch
        val = json_data.(key);
    end
end

%todo: three functions can be combined in a single function
function val = get_constant_term(json_data_xm, json_data_xnm, json_data_rxa)
    fields = fieldnames(json_data_rxa);
    val = 0;
    for k=1:length(fields)
        xa = fields{k};        
        w_xa = weight(json_data_xm, json_data_xnm, xa);
        r_xa = get_value(json_data_rxa, xa);
        val = val+ w_xa*r_xa*r_xa;
    end
end


function H = construct_H(json_data_xm, json_data_xnm, json_data_rxa)
    fields = fieldnames(json_data_rxa);
    len = length(fields);
    W_arr = zeros(1,len);
    for k=1:len
        xa = fields{k};        
        W_arr(k) = 2*weight(json_data_xm, json_data_xnm, xa);
    end
    H = diag(W_arr);
end

function f_t = construct_f_transpose(json_data_xa_m,json_data_xa_nm, json_data_rxa)
    fields = fieldnames(json_data_rxa);
    len = length(fields);
    f_t = zeros(1, len);
    for k=1:len
        xa = fields{k};        
        w_xa = weight(json_data_xa_m, json_data_xa_nm, xa);
        r_xa = get_value(json_data_rxa, xa);
        f_t(k) = -w_xa*r_xa;
    end
end
