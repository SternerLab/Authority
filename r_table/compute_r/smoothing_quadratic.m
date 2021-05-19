format long
json_data_rxa = get_json_object('results/r_xa.json'); 
json_data_xa_m = get_json_object('results/xa_m.json');
json_data_xa_nm = get_json_object('results/xa_nm.json');
n = length(fieldnames(json_data_rxa));
A = read_from_txt("results/A_matrix.txt");
H = construct_H(json_data_xa_m, json_data_xa_nm, json_data_rxa);
f_t = construct_f_t( json_data_xa_m, json_data_xa_nm, json_data_rxa);
f = transpose(f_t);
b = zeros(length(A),1);
Aeq = zeros(0,n);
beq = zeros(0,1);
iA0 = false(length(A),1);
opt = mpcActiveSetOptions;
[x,exitflag,iA,lambda] = mpcActiveSetSolver(H,f,A,b,Aeq,beq,iA0, opt);
disp(x);
fileID = fopen('results/r_smoothen.txt','w');
fprintf(fileID,'%f\n', x);

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

function A = read_from_txt(filename)
    A = dlmread(filename)
    disp(A)
end


function w_xa = weight(json_data_xa_m,json_data_xa_nm,xa)
    w_xa = json_data_xa_m.(xa)+json_data_xa_nm.(xa);
end


function H = construct_H(json_data_xm, json_data_xnm, json_data_rxa)
    fields = fieldnames(json_data_rxa);
    len = length(fields);
    W_arr = zeros(1,len);
    for k=1:len
        xa = fields{k}; 
        wei = weight(json_data_xm, json_data_xnm, xa);
        W_arr(k) = 2*wei*wei;
    end
    H = diag(W_arr);
%     H = [415020 0 0 ;0 472244 0;0 0 497916];
end


function f_t = construct_f_t(json_data_xa_m,json_data_xa_nm, json_data_rxa)
    fields = fieldnames(json_data_rxa);
    disp(fields);
    len = length(fields);
    f_t = zeros(1, len);
    for k=1:len
        xa = fields{k};  
        disp(xa);
        w_xa = weight(json_data_xa_m, json_data_xa_nm, xa);
        r_xa = get_value(json_data_rxa, xa);
        f_t(k) = -2*w_xa*w_xa*r_xa;
    end
end