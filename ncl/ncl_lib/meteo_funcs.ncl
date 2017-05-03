;
;+---+-----------------------------------------------------------------+
;
; returns saturation vapor pressure (Pa) given temperature (K)
;   with respect to plane surface of water (not ice)
;
        function e_sub_s(temp_K[*][*]:numeric)
        begin
                c = new(9,float)
                c = (/610.5851,44.40316,1.430341,.2641412e-1,.2995057e-3,.2031998e-5,.6936113e-8,.2564861e-11,-.3704404e-13/)
                return ( c(0)+(temp_K-273.16)*(c(1)+(temp_K-273.16)*(c(2)+(temp_K-273.16)*(c(3)+(temp_K-273.16)*(c(4)+(temp_K-273.16)*(c(5)+(temp_K-273.16)*(c(6)+(temp_K-273.16)*(c(7)+(temp_K-273.16)*c(8)))))))) )
        end

;
;+---+-----------------------------------------------------------------+
;
; returns dewpoint temperature (K) given Pressure (Pa) and mixing ratio (kg/kg)
;
        function t_dew(pres_Pa[*][*]:numeric,w_non[*][*]:numeric)
        begin
                dims = dimsizes(pres_Pa)
                es = new((/dims(0),dims(1)/),float)
                es=pres_Pa*w_non/(.622+w_non)
                return ( (35.86*log(es)-4947.2325)/(log(es)-23.6837) )
        end
;
;+---+-----------------------------------------------------------------+
;
; returns LCL temperature (K) given temperature (K) and dewpoint (K)
;
        function t_lcl(temp_K[*][*]:numeric,tdew_K[*][*]:numeric)
        begin
                dims = dimsizes(temp_K)
                denom = new((/dims(0),dims(1)/),float)
                denom= ( 1.0/(tdew_K-56.0) ) + (log(temp_K/tdew_K)/800.)
                return ( ( 1.0 / denom ) + 56.0)
        end
;
;+---+-----------------------------------------------------------------+
;
; returns theta-e (K) given pressure (Pa), temperature (K),
;   mixing ratio (kg/kg), and LCL temperature (K)
;
        function theta_e(pres_Pa[*][*]:numeric,temp_K[*][*]:numeric,w_non[*][*]:numeric,tlcl_K[*][*]:numeric)
        begin
                dims = dimsizes(temp_K)
                xx = new((/dims(0),dims(1)/),float)
                xx = temp_K * (100000.0/pres_Pa)^(0.2854*(1.0 - (0.28*w_non) ))
                return ( xx * exp( ((3.376/tlcl_K) - 0.00254)*((w_non*1000.0) * (1.0 + 0.81*w_non)) ) )
        end
;
;+---+-----------------------------------------------------------------+
;
; returns height (m) given pressure (Pa); assumes standard atmosphere
;
        function std_atmos(pres_Pa:numeric)
        begin
                return(44307.692 * (1.0 - (pres_Pa/101325.0)^0.190))
        end
